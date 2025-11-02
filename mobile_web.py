"""
Aplicación Web Simple - Cámara Móvil
===================================

Versión simplificada que funciona directamente en navegadores móviles.
"""

import flet as ft
import asyncio
import json
import base64
import logging
from typing import Optional


class SimpleMobileApp:
    """Aplicación móvil simple para captura de cámara."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.is_streaming = False
        self.desktop_ip = "192.168.1.100"
        
    def main(self, page: ft.Page):
        """Función principal."""
        # Configurar página para móvil
        page.title = "📱 Cámara IP"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        
        self.page = page
        self._create_interface()
    
    def _create_interface(self):
        """Crea la interfaz móvil."""
        
        # Título
        title = ft.Text(
            "📱 Cámara IP Móvil",
            size=28,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Campo IP
        self.ip_field = ft.TextField(
            label="IP del Desktop",
            hint_text="192.168.1.100",
            value=self.desktop_ip,
            width=280,
            prefix_icon=ft.Icons.COMPUTER,
            text_align=ft.TextAlign.CENTER
        )
        
        # Botones de control de cámara
        self.start_camera_btn = ft.ElevatedButton(
            "📹 Iniciar Cámara",
            icon=ft.Icons.VIDEOCAM,
            on_click=self._start_camera,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_500,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            width=250,
            height=50
        )
        
        self.stop_camera_btn = ft.ElevatedButton(
            "⏹️ Detener Cámara",
            icon=ft.Icons.STOP,
            on_click=self._stop_camera,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_500,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            width=250,
            height=50,
            disabled=True
        )
        
        # Texto de estado
        self.status_text = ft.Text(
            "📱 Listo para conectar",
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_600
        )
        
        # Información de la cámara
        self.camera_info = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "ℹ️ Información",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_800
                    ),
                    ft.Text("• Resolución: 640x480"),
                    ft.Text("• FPS: 10"),
                    ft.Text("• Formato: JPEG"),
                    ft.Text("• Cámara: Trasera")
                ], spacing=8),
                padding=20
            ),
            width=350
        )
        
        # Instrucciones
        instructions = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "📋 Instrucciones",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_800
                    ),
                    ft.Text("1. Introduce la IP de tu PC"),
                    ft.Text("2. Asegúrate de que el Desktop Receiver esté ejecutándose"),
                    ft.Text("3. Presiona 'Iniciar Cámara'"),
                    ft.Text("4. Permite el acceso a la cámara"),
                    ft.Text("5. ¡La transmisión comenzará automáticamente!")
                ], spacing=8),
                padding=20
            ),
            width=350
        )
        
        # Layout principal
        main_column = ft.Column([
            title,
            ft.Divider(height=30),
            self.ip_field,
            ft.Divider(height=20),
            
            # Controles de cámara
            ft.Column([
                self.start_camera_btn,
                self.stop_camera_btn,
                ft.Divider(height=10),
                self.status_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            
            ft.Divider(height=20),
            self.camera_info,
            ft.Divider(height=30),
            instructions
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15)
        
        self.page.add(main_column)

    async def _start_camera(self, e):
        """Inicia la captura de cámara."""
        self.is_streaming = True
        self.start_camera_btn.disabled = True
        self.stop_camera_btn.disabled = False
        self.status_text.value = "🔴 Iniciando cámara..."
        self.status_text.color = ft.Colors.ORANGE_600
        self.page.update()
        
        # Inyectar JavaScript para acceso a la cámara
        js_code = f"""
        var desktopIP = '{self.ip_field.value or "192.168.1.100"}';
        var video = document.createElement('video');
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var stream = null;
        var intervalId = null;
        var frameCount = 0;
        
        // Función para iniciar cámara
        async function startMobileCamera() {{
            try {{
                stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{
                        facingMode: 'environment',
                        width: {{ ideal: 640 }},
                        height: {{ ideal: 480 }}
                    }}
                }});
                
                video.srcObject = stream;
                video.play();
                
                // Esperar a que el video esté listo
                video.onloadedmetadata = function() {{
                    // Crear canvas para captura
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    
                    // Iniciar envío de frames
                    intervalId = setInterval(function() {{
                        if (video.videoWidth > 0) {{
                            ctx.drawImage(video, 0, 0);
                            
                            canvas.toBlob(function(blob) {{
                                if (blob) {{
                                    var reader = new FileReader();
                                    reader.onload = function() {{
                                        sendFrameToDesktop(reader.result);
                                    }};
                                    reader.readAsDataURL(blob);
                                }}
                            }}, 'image/jpeg', 0.8);
                            
                            frameCount++;
                        }}
                    }}, 100); // 10 FPS
                    
                    console.log('Cámara iniciada correctamente');
                }};
                
            }} catch (err) {{
                console.error('Error al acceder a la cámara:', err);
                alert('Error al acceder a la cámara: ' + err.message + '\\n\\nAsegúrate de:\\n1. Permitir acceso a la cámara\\n2. Usar HTTPS o localhost\\n3. Tener una cámara disponible');
            }}
        }}
        
        // Función para enviar frames al desktop
        function sendFrameToDesktop(frameData) {{
            var url = 'http://' + desktopIP + ':8081/frame';
            
            fetch(url, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    frame: frameData,
                    timestamp: Date.now(),
                    frameNumber: frameCount
                }})
            }})
            .then(response => {{
                if (response.ok) {{
                    console.log('Frame enviado correctamente:', frameCount);
                }} else {{
                    console.warn('Error del servidor:', response.status);
                }}
            }})
            .catch(err => {{
                console.error('Error de conexión:', err);
            }});
        }}
        
        // Iniciar la cámara
        startMobileCamera();
        """
        
        try:
            await self.page.evaluate_javascript_async(js_code)
            self.status_text.value = "🔴 Cámara activa - Transmitiendo..."
            self.status_text.color = ft.Colors.RED_600
        except Exception as ex:
            self.status_text.value = f"❌ Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.start_camera_btn.disabled = False
            self.stop_camera_btn.disabled = True
        
        self.page.update()
    
    async def _stop_camera(self, e):
        """Detiene la captura de cámara."""
        self.is_streaming = False
        self.start_camera_btn.disabled = False
        self.stop_camera_btn.disabled = True
        self.status_text.value = "⏸️ Cámara detenida"
        self.status_text.color = ft.Colors.ORANGE_600
        
        # JavaScript para detener la cámara
        js_code = """
        if (typeof stream !== 'undefined' && stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        if (typeof intervalId !== 'undefined' && intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
        
        console.log('Cámara detenida');
        """
        
        try:
            await self.page.evaluate_javascript_async(js_code)
        except Exception as ex:
            print(f"Error deteniendo cámara: {ex}")
        
        self.page.update()


def main(page: ft.Page):
    """Función principal para la app web."""
    app = SimpleMobileApp()
    app.main(page)


if __name__ == "__main__":
    import os
    
    # Obtener puerto de variable de entorno (para deployment)
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando servidor web en http://{host}:{port}")
    print("📱 Abre esta URL en tu móvil para usar la cámara")
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=port,
        host=host,
        web_renderer="canvaskit"  # Mejor compatibilidad en producción
    )