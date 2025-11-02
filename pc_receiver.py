"""
Receptor PC Directo - Ver Cámara del Móvil
==========================================

Esta aplicación se ejecuta en tu PC y te permite ver la transmisión 
de cámara directamente desde tu móvil.

INSTRUCCIONES:
1. Ejecuta este script en tu PC
2. En tu móvil, ve a la URL que te muestre
3. Permite acceso a la cámara
4. ¡Verás la transmisión en tu PC!
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
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import urllib.parse
import socket


class MobileFrameHandler(BaseHTTPRequestHandler):
    """Maneja los frames enviados desde el móvil."""
    
    def do_POST(self):
        """Recibe frames POST desde móvil."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            data = json.loads(post_data.decode('utf-8'))
            
            if 'frame' in data:
                # Pasar frame a la app principal
                if hasattr(self.server, 'app'):
                    self.server.app.process_frame(data['frame'])
                
                # Respuesta exitosa
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            else:
                self.send_error(400, 'No frame data')
                
        except Exception as e:
            print(f"Error en frame handler: {e}")
            self.send_error(500, str(e))
    
    def do_GET(self):
        """Sirve la página web para móviles."""
        if self.path == '/' or self.path == '/mobile':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # HTML para móviles
            html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 Cámara Móvil</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            text-align: center;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 20px;
            margin: 20px auto;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
        }}
        .button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            cursor: pointer;
            margin: 10px;
            width: 80%;
        }}
        .button:hover {{
            transform: scale(1.05);
        }}
        #video {{
            width: 100%;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .status {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 10px;
            font-weight: bold;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
        }}
        .status.error {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">📱 Cámara Móvil ➡️ PC</div>
        
        <button class="button" onclick="startCamera()">
            📹 Iniciar Transmisión
        </button>
        
        <button class="button" onclick="stopCamera()" style="background: #dc3545;">
            ⏹️ Detener
        </button>
        
        <video id="video" autoplay playsinline muted style="display: none;"></video>
        
        <div id="status" class="status">
            Presiona "Iniciar Transmisión" para comenzar
        </div>
        
        <div style="font-size: 0.9em; color: #666; margin-top: 20px;">
            🖥️ Conectado a PC: {self.client_address[0]}
        </div>
    </div>

    <script>
        let stream = null;
        let sending = false;
        let frameCount = 0;

        async function startCamera() {{
            try {{
                document.getElementById('status').innerHTML = '🔄 Iniciando cámara...';
                document.getElementById('status').className = 'status';
                
                stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{
                        facingMode: 'environment',
                        width: {{ ideal: 640 }},
                        height: {{ ideal: 480 }}
                    }}
                }});

                const video = document.getElementById('video');
                video.srcObject = stream;
                video.style.display = 'block';
                
                document.getElementById('status').innerHTML = '✅ Cámara iniciada - Transmitiendo a PC';
                document.getElementById('status').className = 'status success';
                
                // Iniciar envío de frames
                sending = true;
                sendFrames(video);

            }} catch (error) {{
                console.error('Error:', error);
                document.getElementById('status').innerHTML = '❌ Error: ' + error.message;
                document.getElementById('status').className = 'status error';
            }}
        }}

        function sendFrames(video) {{
            if (!sending) return;

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = 640;
            canvas.height = 480;
            
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob(async (blob) => {{
                if (blob && sending) {{
                    const reader = new FileReader();
                    reader.onload = async () => {{
                        try {{
                            const response = await fetch('/frame', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                }},
                                body: JSON.stringify({{
                                    frame: reader.result,
                                    timestamp: Date.now(),
                                    frameNumber: ++frameCount
                                }})
                            }});
                            
                            if (response.ok) {{
                                document.getElementById('status').innerHTML = 
                                    `📡 Transmitiendo - Frame: ${{frameCount}}`;
                            }}
                        }} catch (error) {{
                            console.error('Send error:', error);
                        }}
                    }};
                    reader.readAsDataURL(blob);
                }}
            }}, 'image/jpeg', 0.8);

            // Siguiente frame
            setTimeout(() => sendFrames(video), 100); // 10 FPS
        }}

        function stopCamera() {{
            sending = false;
            
            if (stream) {{
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }}
            
            document.getElementById('video').style.display = 'none';
            document.getElementById('status').innerHTML = '⏸️ Transmisión detenida';
            document.getElementById('status').className = 'status';
        }}
    </script>
</body>
</html>"""
            
            self.wfile.write(html.encode())
        
        elif self.path == '/frame':
            # Para requests POST de frames, redirigir al handler POST
            self.do_POST()
        
        else:
            self.send_error(404, 'Not found')
    
    def do_OPTIONS(self):
        """Maneja preflight CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Silencia logs del servidor."""
        pass


class PCReceiverApp:
    """Aplicación PC que recibe cámara desde móvil."""
    
    def __init__(self):
        """Inicializa la app."""
        self.current_frame = None
        self.frame_count = 0
        self.server = None
        self.server_thread = None
        self.is_recording = False
        self.video_writer = None
        
    def run(self, page: ft.Page):
        """Ejecuta la aplicación."""
        page.title = "🖥️ Receptor Cámara Móvil"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Configurar ventana
        if hasattr(page, 'window') and page.window:
            page.window.width = 900
            page.window.height = 700
            page.window.center()
        
        self.page = page
        self._create_interface()
        self._start_frame_updater()
    
    def _create_interface(self):
        """Crea la interfaz."""
        
        # Título
        title = ft.Text(
            "🖥️ Receptor Cámara Móvil",
            size=24,
            weight=ft.FontWeight.BOLD
        )
        
        # IP Info
        local_ip = self._get_local_ip()
        
        # Controles servidor
        self.start_btn = ft.ElevatedButton(
            "🚀 Iniciar Servidor",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._start_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_500, color=ft.Colors.WHITE)
        )
        
        self.stop_btn = ft.ElevatedButton(
            "⏹️ Detener Servidor", 
            icon=ft.Icons.STOP,
            on_click=self._stop_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE),
            disabled=True
        )
        
        # Video display
        self.video_view = ft.Image(
            src="",
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(8)
        )
        
        # Placeholder
        self.no_signal = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VIDEOCAM_OFF, size=60, color=ft.Colors.GREY_400),
                ft.Text("Esperando móvil...", size=16, color=ft.Colors.GREY_600),
                ft.Text("Inicia el servidor primero", size=12, color=ft.Colors.GREY_500)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=640,
            height=480,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.all(8),
            alignment=ft.alignment.center
        )
        
        # Controles de grabación
        self.record_btn = ft.ElevatedButton(
            "🔴 Grabar",
            icon=ft.Icons.VIDEOCAM,
            on_click=self._toggle_recording,
            disabled=True
        )
        
        self.photo_btn = ft.ElevatedButton(
            "📸 Foto",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self._take_photo,
            disabled=True
        )
        
        # Estado
        self.status_text = ft.Text(
            "⏸️ Servidor detenido",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        self.stats_text = ft.Text(
            "Frames: 0",
            size=12,
            color=ft.Colors.GREY_500
        )
        
        # Instrucciones
        self.instructions = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📱 INSTRUCCIONES:", weight=ft.FontWeight.BOLD),
                    ft.Text("1. Haz clic en 'Iniciar Servidor'"),
                    ft.Text("2. En tu móvil, ve a:"),
                    ft.Text(f"   http://{local_ip}:8080", 
                           color=ft.Colors.BLUE_600, weight=ft.FontWeight.BOLD),
                    ft.Text("3. Permite acceso a la cámara"),
                    ft.Text("4. Haz clic en 'Iniciar Transmisión'"),
                    ft.Text("5. ¡Verás la cámara aquí!"),
                ], spacing=5),
                padding=15
            )
        )
        
        # Layout principal
        main_column = ft.Column([
            title,
            ft.Divider(height=20),
            
            # Controles servidor
            ft.Row([
                self.start_btn,
                self.stop_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(height=10),
            
            # Video
            ft.Container(
                content=ft.Stack([
                    self.no_signal,
                    self.video_view
                ]),
                alignment=ft.alignment.center
            ),
            
            # Controles grabación
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
            self.instructions
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
        self.page.add(main_column)
    
    def _get_local_ip(self):
        """Obtiene IP local."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def _start_server(self, e):
        """Inicia el servidor HTTP."""
        try:
            self.server = HTTPServer(('', 8080), MobileFrameHandler)
            self.server.app = self  # Referencia a esta app
            
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            # Actualizar UI
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
            self.record_btn.disabled = False
            self.photo_btn.disabled = False
            
            local_ip = self._get_local_ip()
            self.status_text.value = f"🟢 Servidor activo en http://{local_ip}:8080"
            self.status_text.color = ft.Colors.GREEN_600
            
            self.page.update()
            
        except Exception as ex:
            self.status_text.value = f"❌ Error: {ex}"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()
    
    def _stop_server(self, e):
        """Detiene el servidor."""
        if self.server:
            self.server.shutdown()
            self.server = None
        
        # Detener grabación si está activa
        if self.is_recording:
            self._toggle_recording(None)
        
        # Actualizar UI
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.record_btn.disabled = True
        self.photo_btn.disabled = True
        
        self.status_text.value = "⏸️ Servidor detenido"
        self.status_text.color = ft.Colors.GREY_600
        
        self.page.update()
    
    def _toggle_recording(self, e):
        """Inicia/detiene grabación."""
        if not self.is_recording:
            # Iniciar grabación
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/mobile_direct_{timestamp}.mp4"
            Path("recordings").mkdir(exist_ok=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 10.0, (640, 480))
            
            self.is_recording = True
            self.record_btn.text = "⏹️ Detener Grabación"
            self.record_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
        else:
            # Detener grabación
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            self.is_recording = False
            self.record_btn.text = "🔴 Grabar"
            self.record_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_500, color=ft.Colors.WHITE)
        
        self.page.update()
    
    def _take_photo(self, e):
        """Captura foto."""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photos/mobile_direct_{timestamp}.jpg"
            Path("photos").mkdir(exist_ok=True)
            
            cv2.imwrite(filename, self.current_frame)
            
            self.status_text.value = f"📸 Foto guardada: {filename}"
            self.status_text.color = ft.Colors.BLUE_600
            self.page.update()
    
    def process_frame(self, frame_data):
        """Procesa frame recibido del móvil."""
        try:
            # Decodificar base64
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            
            img_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                self.current_frame = cv2.resize(frame, (640, 480))
                self.frame_count += 1
                return True
                
        except Exception as e:
            print(f"Error procesando frame: {e}")
        
        return False
    
    def _start_frame_updater(self):
        """Inicia actualizador de frames."""
        def update_frames():
            while True:
                try:
                    if self.current_frame is not None:
                        # Grabar si está activo
                        if self.is_recording and self.video_writer:
                            self.video_writer.write(self.current_frame)
                        
                        # Convertir a base64 para mostrar
                        _, buffer = cv2.imencode('.jpg', self.current_frame)
                        img_b64 = base64.b64encode(buffer).decode()
                        
                        # Actualizar UI
                        def update_ui():
                            self.video_view.src_base64 = f"data:image/jpeg;base64,{img_b64}"
                            self.video_view.update()
                            
                            self.status_text.value = "🔴 Recibiendo video del móvil"
                            self.status_text.color = ft.Colors.RED_600
                            
                            self.stats_text.value = f"Frames recibidos: {self.frame_count}"
                            self.stats_text.update()
                        
                        self.page.invoke_later(update_ui)
                    
                    time.sleep(0.033)  # ~30 FPS
                    
                except Exception as e:
                    print(f"Error en frame updater: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=update_frames, daemon=True)
        thread.start()


if __name__ == "__main__":
    print("🖥️ Iniciando Receptor PC Directo...")
    
    # Crear directorios
    Path("recordings").mkdir(exist_ok=True)
    Path("photos").mkdir(exist_ok=True)
    
    # Ejecutar app
    app = PCReceiverApp()
    ft.app(target=app.run)