"""
Gestor de streams de cámara mejorado basado en OpenCV.
"""

import base64
import threading
import time
import logging
import cv2
import requests
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

import flet as ft

from src.utils.helpers import build_stream_url, format_duration, format_bytes


@dataclass
class StreamInfo:
    """Información sobre un stream de cámara."""
    url: str
    fps: float = 0.0
    resolution: tuple = (0, 0)
    codec: str = ""
    bitrate: float = 0.0
    duration: float = 0.0
    frames_captured: int = 0
    bytes_received: int = 0


class StreamRecorder:
    """Grabador de video para streams de cámara."""
    
    def __init__(self, output_path: Path, fps: float = 15.0, codec: str = 'mp4v'):
        """
        Inicializa el grabador.
        
        Args:
            output_path: Ruta del archivo de salida
            fps: FPS de grabación
            codec: Codec de video
        """
        self.output_path = output_path
        self.fps = fps
        self.codec = codec
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self.start_time = None
        self.frame_count = 0
        
    def start(self, frame_size: tuple) -> bool:
        """
        Inicia la grabación.
        
        Args:
            frame_size: Tamaño del frame (width, height)
            
        Returns:
            True si se inició correctamente
        """
        try:
            fourcc = cv2.VideoWriter_fourcc(*self.codec)
            self.writer = cv2.VideoWriter(
                str(self.output_path),
                fourcc,
                self.fps,
                frame_size
            )
            
            if not self.writer.isOpened():
                return False
                
            self.is_recording = True
            self.start_time = time.time()
            self.frame_count = 0
            return True
            
        except Exception as e:
            logging.error(f"Error al iniciar grabación: {e}")
            return False
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Escribe un frame al archivo.
        
        Args:
            frame: Frame a escribir
            
        Returns:
            True si se escribió correctamente
        """
        if not self.is_recording or self.writer is None:
            return False
            
        try:
            self.writer.write(frame)
            self.frame_count += 1
            return True
        except Exception as e:
            logging.error(f"Error al escribir frame: {e}")
            return False
    
    def stop(self) -> Dict[str, Any]:
        """
        Detiene la grabación y retorna estadísticas.
        
        Returns:
            Diccionario con estadísticas de la grabación
        """
        stats = {
            'duration': 0.0,
            'frames': self.frame_count,
            'file_size': 0,
            'success': False
        }
        
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        
        if self.start_time:
            stats['duration'] = time.time() - self.start_time
            
        if self.output_path.exists():
            stats['file_size'] = self.output_path.stat().st_size
            stats['success'] = True
            
        self.is_recording = False
        return stats


class StreamWorker:
    """Trabajador de stream mejorado basado en el código original."""
    
    def __init__(self, page: ft.Page, image_widget: ft.Image, status_callback: Callable[[str, str], None]):
        """
        Inicializa el trabajador de stream.
        
        Args:
            page: Página de Flet
            image_widget: Widget de imagen para mostrar el stream
            status_callback: Callback para actualizar el estado (texto, color)
        """
        self.page = page
        self.image_widget = image_widget
        self.status_callback = status_callback
        self.logger = logging.getLogger(__name__)
        
        # Control de threading
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._cap: Optional[cv2.VideoCapture] = None
        
        # Información del stream
        self.stream_info = StreamInfo(url="")
        self.is_connected = False
        
        # Grabación
        self.recorder: Optional[StreamRecorder] = None
        
        # Estadísticas
        self._last_fps_time = time.time()
        self._fps_counter = 0
        
    def start(self, url: str) -> None:
        """
        Inicia el stream de la cámara.
        
        Args:
            url: URL del stream
        """
        self.stop()  # Detener stream anterior
        self._stop_event.clear()
        self.stream_info.url = url
        
        def run_stream():
            """Función principal del hilo de stream."""
            try:
                # Verificar conectividad rápida
                try:
                    base_url = url.split("/video")[0]
                    response = requests.get(base_url, timeout=3)
                    response.raise_for_status()
                except requests.RequestException:
                    pass  # Continuar de todos modos
                
                # Abrir captura de video
                self._cap = cv2.VideoCapture(url)
                
                if not self._cap.isOpened():
                    raise RuntimeError("No se pudo abrir el stream. Verifica IP, puerto y que IP Webcam esté activo.")
                
                # Configurar propiedades de captura
                self._configure_capture()
                
                self._update_status("Conectado ✔", "green")
                self.is_connected = True
                
                # Loop principal de captura
                self._capture_loop()
                
            except Exception as e:
                self.logger.error(f"Error en stream: {e}")
                self._update_status(f"Error: {e}", "red")
            finally:
                self._cleanup_capture()
                
        self._thread = threading.Thread(target=run_stream, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Detiene el stream."""
        self._stop_event.set()
        self.is_connected = False
        
        # Detener grabación si está activa
        if self.recorder and self.recorder.is_recording:
            self.stop_recording()
        
        # Limpiar captura
        self._cleanup_capture()
        
        # Esperar a que termine el hilo
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        
        self._update_status("Detenido", "grey")
    
    def start_recording(self, filename: Optional[str] = None) -> bool:
        """
        Inicia la grabación del stream.
        
        Args:
            filename: Nombre del archivo (opcional, se genera automáticamente si no se especifica)
            
        Returns:
            True si se inició correctamente
        """
        if not self.is_connected:
            return False
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            
        output_path = Path("recordings") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        # Obtener tamaño del frame actual
        if self._cap:
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.recorder = StreamRecorder(output_path)
            if self.recorder.start((width, height)):
                self.logger.info(f"Grabación iniciada: {output_path}")
                return True
                
        return False
    
    def stop_recording(self) -> Optional[Dict[str, Any]]:
        """
        Detiene la grabación.
        
        Returns:
            Estadísticas de la grabación o None
        """
        if self.recorder and self.recorder.is_recording:
            stats = self.recorder.stop()
            self.logger.info(f"Grabación detenida. Duración: {format_duration(stats['duration'])}")
            return stats
        return None
    
    def capture_photo(self, filename: Optional[str] = None) -> bool:
        """
        Captura una foto del stream actual.
        
        Args:
            filename: Nombre del archivo (opcional)
            
        Returns:
            True si se capturó correctamente
        """
        if not self.is_connected or not self._cap:
            return False
            
        try:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                return False
                
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
                
            output_path = Path("photos") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            # Guardar imagen
            success = cv2.imwrite(str(output_path), frame)
            
            if success:
                self.logger.info(f"Foto capturada: {output_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al capturar foto: {e}")
            
        return False
    
    def _configure_capture(self) -> None:
        """Configura las propiedades de la captura."""
        if not self._cap:
            return
            
        try:
            # Configurar buffer para reducir latencia
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Obtener información del stream
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self._cap.get(cv2.CAP_PROP_FPS)
            
            self.stream_info.resolution = (width, height)
            self.stream_info.fps = fps if fps > 0 else 15.0
            
            self.logger.info(f"Stream configurado: {width}x{height} @ {self.stream_info.fps} FPS")
            
        except Exception as e:
            self.logger.warning(f"No se pudo configurar completamente la captura: {e}")
    
    def _capture_loop(self) -> None:
        """Loop principal de captura de frames."""
        while not self._stop_event.is_set():
            try:
                ret, frame = self._cap.read()
                
                if not ret or frame is None:
                    self._update_status("Sin datos de video…", "amber")
                    time.sleep(0.2)
                    continue
                
                # Procesar frame
                self._process_frame(frame)
                
                # Actualizar estadísticas
                self._update_statistics()
                
                # Control de FPS
                time.sleep(0.033)  # ~30 FPS máximo
                
            except Exception as e:
                self.logger.error(f"Error en loop de captura: {e}")
                break
    
    def _process_frame(self, frame: np.ndarray) -> None:
        """
        Procesa un frame capturado.
        
        Args:
            frame: Frame a procesar
        """
        try:
            # Grabar si está activo
            if self.recorder and self.recorder.is_recording:
                self.recorder.write_frame(frame)
            
            # Convertir para mostrar en Flet
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Codificar a PNG
            success, buffer = cv2.imencode('.png', rgb_frame)
            if not success:
                return
                
            # Convertir a base64
            b64_string = base64.b64encode(buffer.tobytes()).decode('ascii')
            
            # Actualizar widget de imagen
            def update_image():
                self.image_widget.src_base64 = f"data:image/png;base64,{b64_string}"
                self.image_widget.update()
                
            self.page.invoke_later(update_image)
            
        except Exception as e:
            self.logger.error(f"Error al procesar frame: {e}")
    
    def _update_statistics(self) -> None:
        """Actualiza las estadísticas del stream."""
        self.stream_info.frames_captured += 1
        self._fps_counter += 1
        
        # Calcular FPS real cada segundo
        current_time = time.time()
        if current_time - self._last_fps_time >= 1.0:
            actual_fps = self._fps_counter / (current_time - self._last_fps_time)
            self.stream_info.fps = actual_fps
            
            self._fps_counter = 0
            self._last_fps_time = current_time
    
    def _cleanup_capture(self) -> None:
        """Limpia recursos de captura."""
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
    
    def _update_status(self, text: str, color: str) -> None:
        """
        Actualiza el estado del stream.
        
        Args:
            text: Texto del estado
            color: Color del texto
        """
        def update():
            self.status_callback(text, color)
            
        self.page.invoke_later(update)


class StreamManager:
    """Gestor principal de streams de cámara."""
    
    def __init__(self):
        """Inicializa el gestor de streams."""
        self.logger = logging.getLogger(__name__)
        self.workers: Dict[str, StreamWorker] = {}
        
    def create_worker(self, name: str, page: ft.Page, image_widget: ft.Image, 
                     status_callback: Callable[[str, str], None]) -> StreamWorker:
        """
        Crea un nuevo worker de stream.
        
        Args:
            name: Nombre del worker
            page: Página de Flet
            image_widget: Widget de imagen
            status_callback: Callback de estado
            
        Returns:
            Worker creado
        """
        if name in self.workers:
            self.workers[name].stop()
            
        worker = StreamWorker(page, image_widget, status_callback)
        self.workers[name] = worker
        return worker
    
    def get_worker(self, name: str) -> Optional[StreamWorker]:
        """
        Obtiene un worker por nombre.
        
        Args:
            name: Nombre del worker
            
        Returns:
            Worker o None si no existe
        """
        return self.workers.get(name)
    
    def stop_all_streams(self) -> None:
        """Detiene todos los streams activos."""
        for worker in self.workers.values():
            worker.stop()
        self.workers.clear()