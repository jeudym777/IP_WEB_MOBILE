"""
Aplicación Web de Cámara IP - Versión Móvil
===========================================

Aplicación web que captura la cámara del teléfono y transmite al desktop.
"""

import base64
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

import flet as ft


class MobileCameraApp:
    """Aplicación principal para captura de cámara móvil."""
    
    def __init__(self):
        """Inicializa la aplicación móvil."""
        self.is_streaming = False
        self.stream_quality = "medium"
        self.server_ip = "192.168.1.100"  # IP del desktop
        
    async def main(self, page: ft.Page):
        """
        Función principal de la aplicación web.
        
        Args:
            page: Página de Flet
        """
        # Configurar página para móvil
        page.title = "📱 Cámara Móvil IP"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 10
        page.scroll = ft.ScrollMode.AUTO
        page.adaptive = True
        
        # Variables de control
        self.page = page
        
        # Crear interfaz móvil
        await self._create_mobile_interface()
        
    async def _create_mobile_interface(self):
        """Crea la interfaz optimizada para móvil."""
        
        # Título principal
        title = ft.Text(
            "📱 Cámara IP Móvil",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Vista previa de la cámara
        self.camera_preview = ft.Image(
            src="",
            width=300,
            height=200,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10)
        )
        
        # Placeholder cuando no hay cámara
        self.no_camera_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CAMERA_ALT, size=50, color=ft.Colors.GREY_400),
                ft.Text("Toca 'Iniciar Cámara' para comenzar", 
                       text_align=ft.TextAlign.CENTER,
                       color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=300,
            height=200,
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center
        )
        
        # Configuración del servidor
        self.server_field = ft.TextField(
            label="IP del Desktop",
            hint_text="192.168.1.100",
            value=self.server_ip,
            width=250,
            prefix_icon=ft.Icons.COMPUTER
        )
        
        # Control de calidad
        self.quality_dropdown = ft.Dropdown(
            label="Calidad",
            value=self.stream_quality,
            options=[
                ft.dropdown.Option("low", "Baja (480p)"),
                ft.dropdown.Option("medium", "Media (720p)"),
                ft.dropdown.Option("high", "Alta (1080p)")
            ],
            width=200
        )
        
        # Botones de control
        self.start_button = ft.ElevatedButton(
            "📹 Iniciar Cámara",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._start_camera,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_500,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            width=200,
            height=50
        )
        
        self.stop_button = ft.ElevatedButton(
            "⏹️ Detener",
            icon=ft.Icons.STOP,
            on_click=self._stop_camera,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_500,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            width=200,
            height=50,
            disabled=True
        )
        
        # Estado de conexión
        self.status_text = ft.Text(
            "📱 Listo para transmitir",
            size=16,
            color=ft.Colors.BLUE_600,
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500
        )
        
        # Información de uso
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("ℹ️ Instrucciones:", weight=ft.FontWeight.BOLD),
                    ft.Text("1. Ingresa la IP de tu computadora"),
                    ft.Text("2. Selecciona la calidad deseada"),
                    ft.Text("3. Presiona 'Iniciar Cámara'"),
                    ft.Text("4. Permite el acceso a la cámara"),
                    ft.Text("5. ¡Tu desktop recibirá la señal!"),
                ], spacing=5),
                padding=15
            )
        )
        
        # JavaScript para captura de cámara
        camera_js = """
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'environment',  // Cámara trasera por defecto
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    } 
                });
                
                const video = document.getElementById('camera-video');
                if (!video) {
                    const videoElement = document.createElement('video');
                    videoElement.id = 'camera-video';
                    videoElement.style.display = 'none';
                    document.body.appendChild(videoElement);
                }
                
                const videoElement = document.getElementById('camera-video');
                videoElement.srcObject = stream;
                videoElement.play();
                
                // Capturar frames y enviar
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                setInterval(() => {
                    if (videoElement.videoWidth > 0) {
                        canvas.width = videoElement.videoWidth;
                        canvas.height = videoElement.videoHeight;
                        ctx.drawImage(videoElement, 0, 0);
                        
                        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
                        // Enviar frame al backend
                        window.parent.postMessage({
                            type: 'camera_frame',
                            data: dataUrl
                        }, '*');
                    }
                }, 100); // 10 FPS
                
                return true;
            } catch (err) {
                console.error('Error accessing camera:', err);
                alert('No se pudo acceder a la cámara: ' + err.message);
                return false;
            }
        }
        
        async function stopCamera() {
            const video = document.getElementById('camera-video');
            if (video && video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }
        }
        """
        
        # HTML para la cámara web
        camera_html = ft.Html(
            f"""
            <div id="camera-container" style="text-align: center;">
                <video id="camera-video" autoplay playsinline style="max-width: 100%; border-radius: 10px;"></video>
            </div>
            <script>
                {camera_js}
                
                // Escuchar mensajes del JavaScript
                window.addEventListener('message', function(event) {{
                    if (event.data.type === 'camera_frame') {{
                        // Aquí se procesaría el frame
                        console.log('Frame recibido');
                    }}
                }});
            </script>
            """,
            width=300,
            height=200
        )
        
        # Layout principal
        main_column = ft.Column([
            title,
            ft.Divider(height=20),
            
            # Vista de cámara
            ft.Container(
                content=ft.Stack([
                    self.no_camera_container,
                    camera_html
                ]),
                alignment=ft.alignment.center
            ),
            
            ft.Divider(height=10),
            
            # Configuración
            ft.Row([
                self.server_field,
                self.quality_dropdown
            ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            
            ft.Divider(height=10),
            
            # Controles
            ft.Row([
                self.start_button,
                self.stop_button
            ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            
            ft.Divider(height=10),
            
            # Estado
            self.status_text,
            
            ft.Divider(height=20),
            
            # Información
            info_card
            
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
        spacing=10)
        
        # Agregar a la página
        self.page.add(main_column)
    
    async def _start_camera(self, e):
        """Inicia la captura de cámara."""
        try:
            self.is_streaming = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_text.value = "🔴 Transmitiendo..."
            self.status_text.color = ft.Colors.RED_600
            
            # Ejecutar JavaScript para iniciar cámara
            await self.page.run_javascript_async("startCamera()")
            
            self.page.update()
            
        except Exception as ex:
            self.status_text.value = f"❌ Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()
    
    async def _stop_camera(self, e):
        """Detiene la captura de cámara."""
        try:
            self.is_streaming = False
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.status_text.value = "⏸️ Transmisión detenida"
            self.status_text.color = ft.Colors.ORANGE_600
            
            # Ejecutar JavaScript para detener cámara
            await self.page.run_javascript_async("stopCamera()")
            
            self.page.update()
            
        except Exception as ex:
            self.status_text.value = f"❌ Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.page.update()


# Función principal para la aplicación web
async def main(page: ft.Page):
    """Función principal para la aplicación web."""
    app = MobileCameraApp()
    await app.main(page)


if __name__ == "__main__":
    # Ejecutar como aplicación web
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)