"""
Servidor Desktop - Receptor de Cámara Móvil
==========================================

Aplicación desktop que recibe la señal de cámara desde el móvil.
"""

import base64
import json
import logging
import asyncio
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

import flet as ft
import cv2
import numpy as np


class CameraReceiver:
    """Receptor de frames de cámara desde dispositivos móviles."""
    
    def __init__(self):
        """Inicializa el receptor."""
        self.is_receiving = False
        self.current_frame = None
        self.frame_count = 0
        self.server = None
        self.server_thread = None
        
    def start_server(self, port: int = 8081):
        """Inicia el servidor HTTP para recibir frames."""
        try:
            self.server = HTTPServer(('', port), CameraHandler)
            self.server.receiver = self  # Referencia al receptor
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            self.is_receiving = True
            return True
            
        except Exception as e:
            logging.error(f"Error iniciando servidor: {e}")
            return False
    
    def stop_server(self):
        """Detiene el servidor."""
        self.is_receiving = False
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.server_thread:
            self.server_thread.join(timeout=1)
    
    def process_frame(self, frame_data: str):
        """
        Procesa un frame recibido del móvil.
        
        Args:
            frame_data: Frame en formato base64
        """
        try:
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


class CameraHandler(BaseHTTPRequestHandler):
    """Handler HTTP para recibir frames de cámara."""
    
    def do_POST(self):
        """Maneja requests POST con frames."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parsear datos
            data = json.loads(post_data.decode('utf-8'))
            
            if 'frame' in data:
                # Procesar frame
                success = self.server.receiver.process_frame(data['frame'])
                
                if success:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok'}).encode())
                else:
                    self.send_error(400, 'Error processing frame')
            else:
                self.send_error(400, 'No frame data')
                
        except Exception as e:
            logging.error(f"Error en handler: {e}")
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Maneja requests OPTIONS para CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suprime logs del servidor HTTP."""
        pass


class DesktopReceiverApp:
    """Aplicación desktop que recibe streams de móviles."""
    
    def __init__(self):
        """Inicializa la aplicación desktop."""
        self.receiver = CameraReceiver()
        self.is_recording = False
        self.video_writer = None
        
    def run(self, page: ft.Page):
        """
        Ejecuta la aplicación desktop.
        
        Args:
            page: Página de Flet
        """
        # Configurar página
        page.title = "🖥️ Receptor de Cámara IP"
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
        """Crea la interfaz desktop."""
        
        # Título
        title = ft.Text(
            "🖥️ Receptor de Cámara IP Móvil",
            size=24,
            weight=ft.FontWeight.BOLD
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
                ft.Icon(ft.Icons.VIDEOCAM_OFF, size=60, color=ft.Colors.GREY_400),
                ft.Text("Esperando señal del móvil...", 
                       size=16,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_600),
                ft.Text("Abre la app web en tu móvil:", 
                       size=12,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_500),
                ft.Text("http://[IP_DESKTOP]:8080", 
                       size=14,
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.BLUE_600,
                       weight=ft.FontWeight.BOLD)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=640,
            height=480,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.all(8),
            alignment=ft.alignment.center
        )
        
        # Información de conexión
        local_ip = self._get_local_ip()
        self.connection_info = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📱 Instrucciones de Conexión:", weight=ft.FontWeight.BOLD),
                    ft.Text(f"1. Conecta tu móvil a la misma red WiFi"),
                    ft.Text(f"2. Abre el navegador en tu móvil"),
                    ft.Text(f"3. Ve a: http://{local_ip}:8080"),
                    ft.Text(f"4. Permite acceso a la cámara"),
                    ft.Text(f"5. ¡Verás la imagen aquí!"),
                    ft.Divider(height=10),
                    ft.Text(f"🌐 IP del servidor: {local_ip}:8081", 
                           weight=ft.FontWeight.BOLD,
                           color=ft.Colors.BLUE_600),
                ], spacing=5),
                padding=15
            )
        )
        
        # Controles
        self.start_server_btn = ft.ElevatedButton(
            "🚀 Iniciar Servidor",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._start_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_500, color=ft.Colors.WHITE)
        )
        
        self.stop_server_btn = ft.ElevatedButton(
            "⏹️ Detener Servidor",
            icon=ft.Icons.STOP,
            on_click=self._stop_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
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
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
        # Estado
        self.status_text = ft.Text(
            "⏸️ Servidor detenido",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        self.stats_text = ft.Text(
            "Frames: 0 | FPS: 0",
            size=12,
            color=ft.Colors.GREY_500
        )
        
        # Layout
        main_column = ft.Column([
            title,
            ft.Divider(height=20),
            
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
                self.start_server_btn,
                self.stop_server_btn,
                self.record_btn,
                self.photo_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            # Estado
            ft.Column([
                self.status_text,
                self.stats_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            
            ft.Divider(height=20),
            
            # Información de conexión
            self.connection_info
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
        self.page.add(main_column)
    
    def _get_local_ip(self) -> str:
        """Obtiene la IP local."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def _start_server(self, e):
        """Inicia el servidor receptor."""
        if self.receiver.start_server():
            self.start_server_btn.disabled = True
            self.stop_server_btn.disabled = False
            self.record_btn.disabled = False
            self.photo_btn.disabled = False
            
            self.status_text.value = "🟢 Servidor activo - Esperando conexiones..."
            self.status_text.color = ft.Colors.GREEN_600
            
            self.page.update()
    
    def _stop_server(self, e):
        """Detiene el servidor receptor."""
        self.receiver.stop_server()
        
        self.start_server_btn.disabled = False
        self.stop_server_btn.disabled = True
        self.record_btn.disabled = True
        self.photo_btn.disabled = True
        
        self.status_text.value = "⏸️ Servidor detenido"
        self.status_text.color = ft.Colors.GREY_600
        
        self.page.update()
    
    def _toggle_recording(self, e):
        """Alterna grabación de video."""
        if not self.is_recording:
            # Iniciar grabación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/mobile_stream_{timestamp}.mp4"
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
        frame = self.receiver.get_latest_frame()
        if frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photos/mobile_photo_{timestamp}.jpg"
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
                    if self.receiver.is_receiving:
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
                                    self.status_text.value = "🔴 Recibiendo video del móvil"
                                    self.status_text.color = ft.Colors.RED_600
                            
                            self.page.invoke_later(update_ui)
                        
                        # Calcular FPS
                        current_time = time.time()
                        if current_time - last_time >= 1.0:
                            fps = (self.receiver.frame_count - last_frame_count) / (current_time - last_time)
                            
                            def update_stats():
                                self.stats_text.value = f"Frames: {self.receiver.frame_count} | FPS: {fps:.1f}"
                                self.stats_text.update()
                            
                            self.page.invoke_later(update_stats)
                            
                            last_frame_count = self.receiver.frame_count
                            last_time = current_time
                    
                    time.sleep(0.033)  # ~30 FPS
                    
                except Exception as e:
                    logging.error(f"Error en actualizador de frames: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=update_frames, daemon=True)
        thread.start()


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear directorios
    Path("recordings").mkdir(exist_ok=True)
    Path("photos").mkdir(exist_ok=True)
    
    # Ejecutar aplicación
    app = DesktopReceiverApp()
    ft.app(target=app.run)