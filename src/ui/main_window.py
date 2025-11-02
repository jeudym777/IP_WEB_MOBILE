"""
Ventana principal de la aplicación de cámara IP.
"""

import logging
from typing import Optional, List, Dict, Any

import flet as ft

from src.ui.components.theme_manager import ThemeManager, AppTheme
from src.camera.stream_manager import StreamManager, StreamWorker
from src.network.discovery import NetworkDiscovery, CameraDevice
from src.utils.config_manager import ConfigManager, CameraConfig
from src.utils.helpers import build_stream_url, parse_ip_port


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self, page: ft.Page, app: Any, theme_manager: ThemeManager,
                 stream_manager: StreamManager, network_discovery: NetworkDiscovery,
                 config_manager: ConfigManager):
        """
        Inicializa la ventana principal.
        
        Args:
            page: Página de Flet
            app: Instancia de la aplicación principal
            theme_manager: Gestor de temas
            stream_manager: Gestor de streams
            network_discovery: Servicio de descubrimiento
            config_manager: Gestor de configuración
        """
        self.page = page
        self.app = app
        self.theme_manager = theme_manager
        self.stream_manager = stream_manager
        self.network_discovery = network_discovery
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Componentes de la UI
        self.ip_field: Optional[ft.TextField] = None
        self.path_dropdown: Optional[ft.Dropdown] = None
        self.status_text: Optional[ft.Text] = None
        self.image_view: Optional[ft.Image] = None
        self.control_buttons: Dict[str, ft.ElevatedButton] = {}
        
        # Worker actual
        self.current_worker: Optional[StreamWorker] = None
        
        # Estado de la aplicación
        self.is_recording = False
        self.discovered_devices: List[CameraDevice] = []
    
    def build(self) -> None:
        """Construye la interfaz de usuario."""
        # Limpiar página
        self.page.controls.clear()
        
        # Crear componentes principales
        self._create_header()
        self._create_connection_panel()
        self._create_control_panel()
        self._create_stream_view()
        self._create_status_bar()
        
        # Agregar todo a la página
        main_column = ft.Column(
            controls=[
                self._get_header(),
                ft.Divider(height=1),
                self._get_connection_panel(),
                self._get_control_panel(),
                self._get_stream_view(),
                ft.Divider(height=1),
                self._get_status_bar(),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        
        self.page.add(main_column)
        self.page.update()
    
    def _create_header(self) -> None:
        """Crea el encabezado de la aplicación."""
        self.title_text = ft.Text(
            "Cámara IP Avanzada",
            size=24,
            weight=ft.FontWeight.BOLD
        )
        
        self.theme_button = ft.IconButton(
            icon=ft.Icons.BRIGHTNESS_6,
            tooltip="Cambiar tema",
            on_click=self._on_theme_toggle
        )
        
        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            tooltip="Configuraciones",
            on_click=self._on_settings_click
        )
    
    def _create_connection_panel(self) -> None:
        """Crea el panel de conexión."""
        self.ip_field = ft.TextField(
            label="IP del dispositivo (IP:PUERTO)",
            hint_text="Ej: 192.168.1.105:8080",
            value="192.168.1.105:8080",
            width=300,
            on_change=self._on_ip_change
        )
        
        self.path_dropdown = ft.Dropdown(
            label="Ruta del stream",
            value="/video",
            options=[
                ft.dropdown.Option("/video", "MJPEG Stream (IP Webcam)"),
                ft.dropdown.Option("/mjpegfeed", "MJPEG Feed"),
                ft.dropdown.Option("/shot.jpg", "Single Frame"),
                ft.dropdown.Option("/cam", "Camera Feed"),
            ],
            width=250,
        )
        
        self.discover_button = ft.ElevatedButton(
            "Buscar Cámaras",
            icon=ft.Icons.SEARCH,
            on_click=self._on_discover_click,
            **self.theme_manager.get_button_style("secondary")
        )
        
        self.connect_button = ft.ElevatedButton(
            "Conectar",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_connect_click,
            **self.theme_manager.get_button_style("primary")
        )
        
        self.disconnect_button = ft.ElevatedButton(
            "Desconectar",
            icon=ft.Icons.STOP,
            on_click=self._on_disconnect_click,
            **self.theme_manager.get_button_style("danger"),
            disabled=True
        )
    
    def _create_control_panel(self) -> None:
        """Crea el panel de control de grabación y fotos."""
        self.record_button = ft.ElevatedButton(
            "Grabar",
            icon=ft.Icons.VIDEOCAM,
            on_click=self._on_record_click,
            **self.theme_manager.get_button_style("success"),
            disabled=True
        )
        
        self.photo_button = ft.ElevatedButton(
            "Foto",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self._on_photo_click,
            **self.theme_manager.get_button_style("primary"),
            disabled=True
        )
        
        self.recordings_button = ft.ElevatedButton(
            "Grabaciones",
            icon=ft.Icons.FOLDER,
            on_click=self._on_recordings_click,
            **self.theme_manager.get_button_style("secondary")
        )
    
    def _create_stream_view(self) -> None:
        """Crea la vista del stream de video."""
        self.image_view = ft.Image(
            src="",
            width=800,
            height=450,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(8)
        )
        
        # Placeholder cuando no hay stream
        self.no_stream_text = ft.Text(
            "No hay stream activo\nConéctate a una cámara para ver la transmisión",
            size=16,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.GREY_600
        )
    
    def _create_status_bar(self) -> None:
        """Crea la barra de estado."""
        self.status_text = ft.Text(
            "Sin conexión",
            size=14,
            color=ft.Colors.GREY_600
        )
        
        self.info_text = ft.Text(
            "Usa una app como 'IP Webcam' en Android para transmitir la cámara por HTTP.",
            size=12,
            color=ft.Colors.GREY_500,
            italic=True
        )
    
    def _get_header(self) -> ft.Row:
        """Obtiene el componente de encabezado."""
        return ft.Row(
            controls=[
                self.title_text,
                ft.Row([
                    self.theme_button,
                    self.settings_button
                ])
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    def _get_connection_panel(self) -> ft.Row:
        """Obtiene el panel de conexión."""
        return ft.Row(
            controls=[
                self.ip_field,
                self.path_dropdown,
                self.discover_button,
                self.connect_button,
                self.disconnect_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )
    
    def _get_control_panel(self) -> ft.Row:
        """Obtiene el panel de control."""
        return ft.Row(
            controls=[
                self.record_button,
                self.photo_button,
                self.recordings_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    
    def _get_stream_view(self) -> ft.Container:
        """Obtiene la vista del stream."""
        return ft.Container(
            content=ft.Stack([
                ft.Container(
                    content=self.no_stream_text,
                    alignment=ft.alignment.center,
                    width=800,
                    height=450,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=ft.border_radius.all(8)
                ),
                self.image_view
            ]),
            alignment=ft.alignment.center
        )
    
    def _get_status_bar(self) -> ft.Column:
        """Obtiene la barra de estado."""
        return ft.Column([
            self.status_text,
            self.info_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Event handlers
    def _on_theme_toggle(self, e) -> None:
        """Maneja el cambio de tema."""
        new_theme = self.theme_manager.toggle_theme(self.page)
        self.config_manager.update_settings(theme=new_theme.value)
    
    def _on_settings_click(self, e) -> None:
        """Maneja el clic en configuraciones."""
        # TODO: Implementar ventana de configuraciones
        self._show_info_dialog("Configuraciones", "Panel de configuraciones próximamente disponible.")
    
    def _on_ip_change(self, e) -> None:
        """Maneja cambios en el campo IP."""
        ip_port = e.control.value
        parsed = parse_ip_port(ip_port)
        
        if parsed:
            self.connect_button.disabled = False
        else:
            self.connect_button.disabled = True if ip_port else False
        
        self.page.update()
    
    def _on_discover_click(self, e) -> None:
        """Maneja la búsqueda automática de cámaras."""
        self.discover_button.disabled = True
        self.discover_button.text = "Buscando..."
        self.page.update()
        
        def on_discovery_complete(devices: List[CameraDevice]):
            """Callback cuando termina el descubrimiento."""
            self.discovered_devices = devices
            
            self.discover_button.disabled = False
            self.discover_button.text = "Buscar Cámaras"
            
            if devices:
                self._show_discovery_results(devices)
            else:
                self._show_info_dialog("Búsqueda", "No se encontraron cámaras en la red local.")
            
            self.page.update()
        
        # Iniciar descubrimiento en segundo plano
        self.network_discovery.start_scan(result_callback=on_discovery_complete)
    
    def _on_connect_click(self, e) -> None:
        """Maneja la conexión a la cámara."""
        ip_port = self.ip_field.value.strip()
        path = self.path_dropdown.value or "/video"
        
        if not ip_port:
            self._update_status("Ingresa IP:PUERTO", "error")
            return
        
        url = build_stream_url(ip_port, path=path)
        
        # Crear worker y conectar
        self.current_worker = self.stream_manager.create_worker(
            "main", self.page, self.image_view, self._update_status
        )
        
        self.current_worker.start(url)
        
        # Actualizar UI
        self.connect_button.disabled = True
        self.disconnect_button.disabled = False
        self.record_button.disabled = False
        self.photo_button.disabled = False
        
        # Guardar conexión reciente
        self.config_manager.add_recent_connection(ip_port)
        
        self._update_status(f"Conectando a {url}...", "info")
        self.page.update()
    
    def _on_disconnect_click(self, e) -> None:
        """Maneja la desconexión."""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker = None
        
        # Restablecer UI
        self.connect_button.disabled = False
        self.disconnect_button.disabled = True
        self.record_button.disabled = True
        self.photo_button.disabled = True
        self.record_button.text = "Grabar"
        self.is_recording = False
        
        # Limpiar imagen
        self.image_view.src_base64 = ""
        
        self._update_status("Desconectado", "neutral")
        self.page.update()
    
    def _on_record_click(self, e) -> None:
        """Maneja la grabación de video."""
        if not self.current_worker:
            return
        
        if not self.is_recording:
            # Iniciar grabación
            if self.current_worker.start_recording():
                self.is_recording = True
                self.record_button.text = "Detener Grabación"
                self.record_button.bgcolor = ft.Colors.RED_500
                self._update_status("Grabando video...", "success")
        else:
            # Detener grabación
            stats = self.current_worker.stop_recording()
            self.is_recording = False
            self.record_button.text = "Grabar"
            self.record_button.bgcolor = self.theme_manager.get_button_style("success")["bgcolor"]
            
            if stats and stats['success']:
                self._update_status(f"Grabación guardada ({stats['frames']} frames)", "success")
            else:
                self._update_status("Error al grabar", "error")
        
        self.page.update()
    
    def _on_photo_click(self, e) -> None:
        """Maneja la captura de fotos."""
        if not self.current_worker:
            return
        
        if self.current_worker.capture_photo():
            self._update_status("Foto capturada", "success")
        else:
            self._update_status("Error al capturar foto", "error")
    
    def _on_recordings_click(self, e) -> None:
        """Maneja la apertura de la carpeta de grabaciones."""
        import os
        import subprocess
        
        recordings_path = "recordings"
        if os.path.exists(recordings_path):
            if os.name == 'nt':  # Windows
                os.startfile(recordings_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", recordings_path])
        else:
            self._show_info_dialog("Grabaciones", "No hay grabaciones disponibles.")
    
    def _update_status(self, text: str, status_type: str) -> None:
        """
        Actualiza el texto de estado.
        
        Args:
            text: Texto a mostrar
            status_type: Tipo de estado (success, error, info, etc.)
        """
        colors = self.theme_manager.get_status_colors()
        color_map = {
            'success': colors['success'],
            'error': colors['error'],
            'info': colors['info'],
            'warning': colors['warning'],
            'neutral': colors['neutral']
        }
        
        self.status_text.value = text
        self.status_text.color = color_map.get(status_type, colors['neutral'])
        self.status_text.update()
    
    def _show_info_dialog(self, title: str, message: str) -> None:
        """Muestra un diálogo informativo."""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._close_dialog(dialog))
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_discovery_results(self, devices: List[CameraDevice]) -> None:
        """Muestra los resultados del descubrimiento."""
        if not devices:
            return
            
        device_options = []
        for device in devices:
            device_options.append(
                ft.ListTile(
                    title=ft.Text(device.name or f"Dispositivo en {device.ip_address}"),
                    subtitle=ft.Text(f"{device.ip_address}:{device.port} - {len(device.services)} servicios"),
                    on_click=lambda e, d=device: self._select_discovered_device(d)
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Cámaras encontradas ({len(devices)})"),
            content=ft.Column(
                controls=device_options,
                height=300,
                scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _select_discovered_device(self, device: CameraDevice) -> None:
        """Selecciona un dispositivo descubierto."""
        self.ip_field.value = f"{device.ip_address}:{device.port}"
        
        # Seleccionar el mejor endpoint disponible
        if "/video" in device.services:
            self.path_dropdown.value = "/video"
        elif device.services:
            self.path_dropdown.value = device.services[0]
            
        self._close_dialog()
        self.page.update()
    
    def _close_dialog(self, dialog=None) -> None:
        """Cierra el diálogo actual."""
        if dialog:
            dialog.open = False
        else:
            if self.page.dialog:
                self.page.dialog.open = False
        self.page.update()