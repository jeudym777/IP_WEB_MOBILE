"""
Receptor PC que se conecta a Cloudflare Worker
==============================================

Esta aplicación se conecta a tu Worker de Cloudflare para recibir
la transmisión de cámara que ya está enviando tu móvil.
"""

import flet as ft
import threading
import time
import json
import base64
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import requests
import socket


class CloudflareReceiver:
    """Receptor que obtiene frames desde Cloudflare Worker."""
    
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
        self.session.timeout = 5
        
    def start_receiving(self):
        """Inicia la recepción de frames."""
        self.is_receiving = True
        
        def receive_loop():
            """Loop principal de recepción."""
            while self.is_receiving:
                try:
                    # Usar el endpoint más eficiente para obtener solo el último frame
                    response = self.session.get(
                        f"{self.worker_url}/api/latest-frame",
                        timeout=3
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('success') and data.get('frame'):
                            frame_info = data['frame']
                            frame_data = frame_info.get('frame', '')
                            if frame_data:
                                self.process_frame(frame_data)
                    
                    # También intentar obtener el stream directo desde la página principal
                    # (esto simula lo que haría un navegador)
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error conectando a Cloudflare: {e}")
                except Exception as e:
                    print(f"Error general: {e}")
                
                time.sleep(0.1)  # 10 FPS polling
        
        # Iniciar thread de recepción
        self.receive_thread = threading.Thread(target=receive_loop, daemon=True)
        self.receive_thread.start()
    
    def stop_receiving(self):
        """Detiene la recepción."""
        self.is_receiving = False
    
    def process_frame(self, frame_data: str):
        """
        Procesa un frame recibido.
        
        Args:
            frame_data: Frame en base64
        """
        try:
            if not frame_data:
                return False
            
            # Limpiar data URL si está presente
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            
            # Decodificar base64
            img_data = base64.b64decode(frame_data)
            
            # Convertir a OpenCV frame
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                self.current_frame = cv2.resize(frame, (640, 480))
                self.frame_count += 1
                return True
                
        except Exception as e:
            print(f"Error procesando frame: {e}")
        
        return False
    
    def get_latest_frame(self):
        """Obtiene el último frame recibido."""
        return self.current_frame
    
    def test_connection(self):
        """Verifica si el Worker está disponible."""
        try:
            response = self.session.get(f"{self.worker_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class CloudflareViewerApp:
    """Aplicación PC que muestra el stream desde Cloudflare."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.receiver = None
        self.is_recording = False
        self.video_writer = None
        
    def run(self, page: ft.Page):
        """Ejecuta la aplicación."""
        page.title = "🌐 Visor Cloudflare Camera"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Configurar ventana
        if hasattr(page, 'window') and page.window:
            page.window.width = 1000
            page.window.height = 750
            page.window.center()
        
        self.page = page
        self._create_interface()
        self._start_frame_updater()
    
    def _create_interface(self):
        """Crea la interfaz de usuario."""
        
        # Título
        title = ft.Text(
            "🌐 Visor Cámara Cloudflare",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_800
        )
        
        # URL del Worker
        self.url_input = ft.TextField(
            label="🔗 URL de tu Worker de Cloudflare",
            hint_text="https://ipwebmobile.tu-usuario.workers.dev",
            width=450,
            value="https://ipwebmobile.jeudym777.workers.dev"  # URL por defecto basada en tu repo
        )
        
        # Botones de conexión
        self.connect_btn = ft.ElevatedButton(
            "🌐 Conectar a Cloudflare",
            icon=ft.Icons.CLOUD,
            on_click=self._connect_to_cloudflare,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=15
            )
        )
        
        self.disconnect_btn = ft.ElevatedButton(
            "❌ Desconectar",
            icon=ft.Icons.CLOUD_OFF,
            on_click=self._disconnect,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE,
                padding=15
            ),
            disabled=True
        )
        
        # Área de video
        self.video_view = ft.Image(
            src="",
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(12)
        )
        
        # Placeholder cuando no hay señal
        self.no_signal_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_OFF, size=80, color=ft.Colors.GREY_400),
                ft.Text("No conectado", 
                       size=18,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_600,
                       weight=ft.FontWeight.BOLD),
                ft.Text("Ingresa la URL de tu Worker y conecta", 
                       size=14,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_500),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text("📱 Asegúrate que tu móvil esté transmitiendo", 
                       size=12,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.ORANGE_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=640,
            height=480,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.all(12),
            alignment=ft.alignment.center,
            border=ft.border.all(2, ft.Colors.GREY_300)
        )
        
        # Controles de captura
        self.record_btn = ft.ElevatedButton(
            "🔴 Grabar Video",
            icon=ft.Icons.VIDEOCAM,
            on_click=self._toggle_recording,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_600,
                color=ft.Colors.WHITE
            ),
            disabled=True
        )
        
        self.photo_btn = ft.ElevatedButton(
            "📸 Capturar Foto",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self._take_photo,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
            disabled=True
        )
        
        # Estado y estadísticas
        self.status_text = ft.Text(
            "⏸️ Desconectado de Cloudflare",
            size=16,
            color=ft.Colors.GREY_600,
            weight=ft.FontWeight.W_500
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
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_600),
                        ft.Text("Instrucciones de Uso", 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_800)
                    ]),
                    ft.Divider(height=10),
                    ft.Text("1. 📱 Asegúrate que tu móvil esté transmitiendo a Cloudflare"),
                    ft.Text("2. 🔗 Verifica que la URL del Worker sea correcta"),
                    ft.Text("3. 🌐 Haz clic en 'Conectar a Cloudflare'"),
                    ft.Text("4. 📺 Verás la transmisión de tu móvil aquí"),
                    ft.Text("5. 🎬 Usa los controles para grabar o capturar fotos"),
                    ft.Divider(height=10),
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ORANGE_600, size=20),
                        ft.Text("Tu móvil debe estar activo y transmitiendo", 
                               color=ft.Colors.ORANGE_800,
                               weight=ft.FontWeight.W_500)
                    ])
                ], spacing=8),
                padding=20
            ),
            elevation=3
        )
        
        # Layout principal
        main_column = ft.Column([
            title,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            
            # Configuración de conexión
            ft.Container(
                content=ft.Row([
                    self.url_input,
                    self.connect_btn,
                    self.disconnect_btn
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
                bgcolor=ft.Colors.BLUE_50,
                padding=20,
                border_radius=ft.border_radius.all(10)
            ),
            
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Área de video
            ft.Container(
                content=ft.Stack([
                    self.no_signal_container,
                    self.video_view
                ]),
                alignment=ft.alignment.center
            ),
            
            ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
            
            # Controles
            ft.Row([
                self.record_btn,
                self.photo_btn
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            
            # Estado
            ft.Column([
                self.status_text,
                self.stats_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Instrucciones
            instructions
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        
        # Agregar con scroll
        self.page.add(
            ft.Column([
                main_column
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _connect_to_cloudflare(self, e):
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
        self.status_text.value = "🔄 Conectando a Cloudflare..."
        self.status_text.color = ft.Colors.ORANGE_600
        self.page.update()
        
        if not self.receiver.test_connection():
            self.status_text.value = "❌ No se puede conectar al Worker"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()
            return
        
        # Iniciar recepción
        self.receiver.start_receiving()
        
        # Actualizar UI para modo conectado
        self.connect_btn.disabled = True
        self.disconnect_btn.disabled = False
        self.record_btn.disabled = False
        self.photo_btn.disabled = False
        self.url_input.disabled = True
        
        self.status_text.value = "🟢 Conectado a Cloudflare - Esperando frames del móvil..."
        self.status_text.color = ft.Colors.GREEN_600
        
        self.page.update()
    
    def _disconnect(self, e):
        """Desconecta del Worker."""
        if self.receiver:
            self.receiver.stop_receiving()
            self.receiver = None
        
        # Detener grabación si está activa
        if self.is_recording:
            self._toggle_recording(None)
        
        # Actualizar UI para modo desconectado
        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True
        self.record_btn.disabled = True
        self.photo_btn.disabled = True
        self.url_input.disabled = False
        
        self.status_text.value = "⏸️ Desconectado de Cloudflare"
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
            self.record_btn.style.bgcolor = ft.Colors.RED_700
            
            self.status_text.value = f"🎥 Grabando video: {filename}"
            self.status_text.color = ft.Colors.RED_600
        else:
            # Detener grabación
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            self.is_recording = False
            self.record_btn.text = "🔴 Grabar Video"
            self.record_btn.style.bgcolor = ft.Colors.ORANGE_600
            
            self.status_text.value = "✅ Grabación completada"
            self.status_text.color = ft.Colors.GREEN_600
        
        self.page.update()
    
    def _take_photo(self, e):
        """Captura una foto del stream."""
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
            else:
                self.status_text.value = "❌ No hay frame disponible para capturar"
                self.status_text.color = ft.Colors.ORANGE_600
                self.page.update()
    
    def _start_frame_updater(self):
        """Inicia el actualizador de frames en la UI."""
        def update_frames():
            last_frame_count = 0
            last_time = time.time()
            
            while True:
                try:
                    if self.receiver and self.receiver.is_receiving:
                        frame = self.receiver.get_latest_frame()
                        
                        if frame is not None:
                            # Grabar si está activo
                            if self.is_recording and self.video_writer:
                                self.video_writer.write(frame)
                            
                            # Convertir a base64 para mostrar en UI
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            img_b64 = base64.b64encode(buffer).decode()
                            
                            # Actualizar UI en thread principal
                            def update_ui():
                                self.video_view.src_base64 = f"data:image/jpeg;base64,{img_b64}"
                                self.video_view.update()
                                
                                # Actualizar estado si no está grabando
                                if not self.is_recording:
                                    self.status_text.value = "🔴 Recibiendo desde móvil vía Cloudflare"
                                    self.status_text.color = ft.Colors.RED_600
                            
                            self.page.invoke_later(update_ui)
                        
                        # Calcular estadísticas cada segundo
                        current_time = time.time()
                        if current_time - last_time >= 1.0:
                            frame_diff = self.receiver.frame_count - last_frame_count
                            fps = frame_diff / (current_time - last_time)
                            
                            def update_stats():
                                self.stats_text.value = f"Frames: {self.receiver.frame_count} | FPS: {fps:.1f}"
                                self.stats_text.update()
                            
                            self.page.invoke_later(update_stats)
                            
                            last_frame_count = self.receiver.frame_count
                            last_time = current_time
                    
                    time.sleep(0.033)  # ~30 FPS check
                    
                except Exception as e:
                    print(f"Error en frame updater: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=update_frames, daemon=True)
        thread.start()


if __name__ == "__main__":
    print("🌐 Iniciando Visor Cloudflare Camera...")
    print("📱 Asegúrate que tu móvil esté transmitiendo")
    
    # Crear directorios
    Path("recordings").mkdir(exist_ok=True)
    Path("photos").mkdir(exist_ok=True)
    
    # Ejecutar aplicación
    app = CloudflareViewerApp()
    ft.app(target=app.run)