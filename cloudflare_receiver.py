"""
Receptor Desktop para Cloudflare Worker
=======================================

Aplicación desktop que recibe frames desde tu Worker de Cloudflare.
Se conecta a tu deployment para ver la cámara del móvil.
"""

import base64
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests
import cv2
import numpy as np
import flet as ft


class CloudflareReceiver:
    """Receptor que se conecta al Worker de Cloudflare."""
    
    def __init__(self, worker_url: str):
        """
        Inicializa el receptor.
        
        Args:
            worker_url: URL del Worker de Cloudflare
        """
        self.worker_url = worker_url.rstrip('/')
        self.is_receiving = False
        self.current_frame = None
        self.frame_count = 0
        self.session = requests.Session()
        
    def start_polling(self):
        """Inicia el polling de frames."""
        self.is_receiving = True
        
        def poll_frames():
            while self.is_receiving:
                try:
                    # Hacer request al API de frames
                    response = self.session.get(
                        f"{self.worker_url}/api/frames",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        frames = data.get('frames', [])
                        
                        # Procesar último frame si hay
                        if frames:
                            latest_frame = frames[-1]
                            self.process_frame(latest_frame.get('frame', ''))
                    
                except Exception as e:
                    logging.error(f"Error polling frames: {e}")
                
                time.sleep(0.1)  # Poll cada 100ms
        
        thread = threading.Thread(target=poll_frames, daemon=True)
        thread.start()
    
    def stop_polling(self):
        """Detiene el polling."""
        self.is_receiving = False
    
    def process_frame(self, frame_data: str):
        """
        Procesa un frame recibido.
        
        Args:
            frame_data: Frame en formato base64
        """
        try:
            if not frame_data:
                return False
                
            # Decodificar base64
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            
            img_data = base64.b64decode(frame_data)
            
            # Convertir a numpy array
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                self.current_frame = frame
                self.frame_count += 1
                return True
                
        except Exception as e:
            logging.error(f"Error procesando frame: {e}")
            
        return False
    
    def get_latest_frame(self):
        """Obtiene el último frame recibido."""
        return self.current_frame
    
    def check_health(self):
        """Verifica si el Worker está disponible."""
        try:
            response = self.session.get(f"{self.worker_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class CloudflareReceiverApp:
    """Aplicación desktop que recibe desde Cloudflare Worker."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.receiver = None
        self.is_recording = False
        self.video_writer = None
        self.worker_url = ""
        
    def run(self, page: ft.Page):
        """
        Ejecuta la aplicación.
        
        Args:
            page: Página de Flet
        """
        # Configurar página
        page.title = "🖥️ Receptor Cloudflare Camera"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.START
        
        # Configurar ventana
        if hasattr(page, 'window') and page.window:
            page.window.width = 1000
            page.window.height = 700
            page.window.center()
        
        self.page = page
        self._create_interface()
        
        # Iniciar actualización de frames
        self._start_frame_updater()
    
    def _create_interface(self):
        """Crea la interfaz."""
        
        # Título
        title = ft.Text(
            "🖥️ Receptor Cámara Cloudflare",
            size=24,
            weight=ft.FontWeight.BOLD
        )
        
        # Configuración de conexión
        self.url_input = ft.TextField(
            label="URL del Worker de Cloudflare",
            hint_text="https://ipwebmobile.tu-usuario.workers.dev",
            width=400,
            value="https://ipwebmobile.jeudym777.workers.dev"  # Ejemplo
        )
        
        self.connect_btn = ft.ElevatedButton(
            "🌐 Conectar",
            icon=ft.Icons.CONNECT_WITHOUT_CONTACT,
            on_click=self._connect_to_worker,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)
        )
        
        self.disconnect_btn = ft.ElevatedButton(
            "❌ Desconectar",
            icon=ft.Icons.CLOSE,
            on_click=self._disconnect,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
        # Vista de video
        self.video_view = ft.Image(
            src="",
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(8)
        )
        
        # Placeholder
        self.no_signal_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_OFF, size=60, color=ft.Colors.GREY_400),
                ft.Text("No conectado al Worker", 
                       size=16,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_600),
                ft.Text("Ingresa la URL de tu Worker y conecta", 
                       size=12,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_500)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=640,
            height=480,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.all(8),
            alignment=ft.alignment.center
        )
        
        # Controles
        self.record_btn = ft.ElevatedButton(
            "🔴 Grabar",
            icon=ft.Icons.VIDEOCAM,
            on_click=self._toggle_recording,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
        self.photo_btn = ft.ElevatedButton(
            "📸 Foto",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self._take_photo,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
        # Estado
        self.status_text = ft.Text(
            "⏸️ Desconectado",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        self.stats_text = ft.Text(
            "Frames: 0 | Estado: Sin conexión",
            size=12,
            color=ft.Colors.GREY_500
        )
        
        # Instrucciones
        instructions = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📱 Instrucciones:", weight=ft.FontWeight.BOLD),
                    ft.Text("1. Asegúrate que tu Worker esté desplegado"),
                    ft.Text("2. Ingresa la URL completa del Worker"),
                    ft.Text("3. Haz clic en 'Conectar'"),
                    ft.Text("4. Abre la URL del Worker en tu móvil"),
                    ft.Text("5. Permite acceso a la cámara"),
                    ft.Text("6. ¡Verás la transmisión aquí!"),
                ], spacing=5),
                padding=15
            )
        )
        
        # Layout
        main_column = ft.Column([
            title,
            ft.Divider(height=20),
            
            # Configuración
            ft.Row([
                self.url_input,
                self.connect_btn,
                self.disconnect_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(height=10),
            
            # Video
            ft.Container(
                content=ft.Stack([
                    self.no_signal_container,
                    self.video_view
                ]),
                alignment=ft.alignment.center
            ),
            
            # Controles
            ft.Row([
                self.record_btn,
                self.photo_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            # Estado
            ft.Column([
                self.status_text,
                self.stats_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Divider(height=20),
            
            # Instrucciones
            instructions
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
        self.page.add(main_column)
    
    def _connect_to_worker(self, e):
        """Conecta al Worker de Cloudflare."""
        url = self.url_input.value.strip()
        
        if not url:
            self.status_text.value = "❌ Ingresa una URL válida"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()
            return
        
        # Crear receptor
        self.receiver = CloudflareReceiver(url)
        
        # Verificar conexión
        if not self.receiver.check_health():
            self.status_text.value = "❌ No se puede conectar al Worker"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()
            return
        
        # Iniciar polling
        self.receiver.start_polling()
        
        # Actualizar UI
        self.connect_btn.disabled = True
        self.disconnect_btn.disabled = False
        self.record_btn.disabled = False
        self.photo_btn.disabled = False
        self.url_input.disabled = True
        
        self.status_text.value = "🟢 Conectado - Esperando frames..."
        self.status_text.color = ft.Colors.GREEN_600
        
        self.worker_url = url
        self.page.update()
    
    def _disconnect(self, e):
        """Desconecta del Worker."""
        if self.receiver:
            self.receiver.stop_polling()
            self.receiver = None
        
        # Detener grabación si está activa
        if self.is_recording:
            self._toggle_recording(None)
        
        # Actualizar UI
        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True
        self.record_btn.disabled = True
        self.photo_btn.disabled = True
        self.url_input.disabled = False
        
        self.status_text.value = "⏸️ Desconectado"
        self.status_text.color = ft.Colors.GREY_600
        
        # Limpiar video
        self.video_view.src_base64 = ""
        self.video_view.update()
        
        self.page.update()
    
    def _toggle_recording(self, e):
        """Alterna grabación de video."""
        if not self.is_recording:
            # Iniciar grabación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/cloudflare_stream_{timestamp}.mp4"
            Path("recordings").mkdir(exist_ok=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 15.0, (640, 480))
            
            self.is_recording = True
            self.record_btn.text = "⏹️ Detener Grabación"
            self.record_btn.style.bgcolor = ft.Colors.RED_600
        else:
            # Detener grabación
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            self.is_recording = False
            self.record_btn.text = "🔴 Grabar"
            self.record_btn.style.bgcolor = ft.Colors.ORANGE_500
        
        self.page.update()
    
    def _take_photo(self, e):
        """Captura una foto."""
        if self.receiver:
            frame = self.receiver.get_latest_frame()
            if frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photos/cloudflare_photo_{timestamp}.jpg"
                Path("photos").mkdir(exist_ok=True)
                
                cv2.imwrite(filename, frame)
                
                self.status_text.value = f"📸 Foto guardada: {filename}"
                self.status_text.color = ft.Colors.BLUE_600
                self.page.update()
    
    def _start_frame_updater(self):
        """Inicia el actualizador de frames."""
        def update_frames():
            last_frame_count = 0
            last_time = time.time()
            
            while True:
                try:
                    if self.receiver and self.receiver.is_receiving:
                        frame = self.receiver.get_latest_frame()
                        
                        if frame is not None:
                            # Redimensionar frame
                            frame_resized = cv2.resize(frame, (640, 480))
                            
                            # Grabar si está activo
                            if self.is_recording and self.video_writer:
                                self.video_writer.write(frame_resized)
                            
                            # Convertir a base64 para mostrar
                            _, buffer = cv2.imencode('.jpg', frame_resized)
                            img_b64 = base64.b64encode(buffer).decode()
                            
                            # Actualizar UI
                            def update_ui():
                                self.video_view.src_base64 = f"data:image/jpeg;base64,{img_b64}"
                                self.video_view.update()
                                
                                # Actualizar estado
                                if self.receiver.frame_count > 0:
                                    self.status_text.value = "🔴 Recibiendo desde Cloudflare"
                                    self.status_text.color = ft.Colors.RED_600
                            
                            self.page.invoke_later(update_ui)
                        
                        # Calcular stats
                        current_time = time.time()
                        if current_time - last_time >= 1.0:
                            frames_diff = self.receiver.frame_count - last_frame_count
                            
                            def update_stats():
                                self.stats_text.value = f"Frames: {self.receiver.frame_count} | Worker: {self.worker_url.split('//')[-1]}"
                                self.stats_text.update()
                            
                            self.page.invoke_later(update_stats)
                            
                            last_frame_count = self.receiver.frame_count
                            last_time = current_time
                    
                    time.sleep(0.1)  # 10 FPS check
                    
                except Exception as e:
                    logging.error(f"Error en actualizador: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=update_frames, daemon=True)
        thread.start()


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear directorios
    Path("recordings").mkdir(exist_ok=True)
    Path("photos").mkdir(exist_ok=True)
    
    print("🖥️ Iniciando Receptor Cloudflare Camera...")
    print("📱 Asegúrate que tu Worker esté desplegado")
    
    # Ejecutar aplicación
    app = CloudflareReceiverApp()
    ft.app(target=app.run)