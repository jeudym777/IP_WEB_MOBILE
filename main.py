"""
Aplicación Principal - Cámara IP Avanzada
=========================================

Aplicación moderna con Flet para visualización y control de cámaras IP móviles.
Incluye funciones avanzadas como grabación, captura de fotos, descubrimiento
automático de red y una interfaz de usuario moderna.
"""

import base64
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

import flet as ft

from src.ui.main_window import MainWindow
from src.ui.components.theme_manager import ThemeManager
from src.camera.stream_manager import StreamManager
from src.network.discovery import NetworkDiscovery
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger


class IPCameraApp:
    """Clase principal de la aplicación de cámara IP."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.logger = setup_logger()
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.stream_manager = StreamManager()
        self.network_discovery = NetworkDiscovery()
        self.main_window: Optional[MainWindow] = None
        
    def run(self, page: ft.Page):
        """
        Ejecuta la aplicación principal.
        
        Args:
            page: La página principal de Flet
        """
        try:
            # Configurar la página principal
            self._configure_page(page)
            
            # Crear la ventana principal
            self.main_window = MainWindow(
                page=page,
                app=self,
                theme_manager=self.theme_manager,
                stream_manager=self.stream_manager,
                network_discovery=self.network_discovery,
                config_manager=self.config_manager
            )
            
            # Inicializar la interfaz
            self.main_window.build()
            
            # Configurar eventos de la ventana
            self._setup_window_events(page)
            
            self.logger.info("Aplicación iniciada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error al iniciar la aplicación: {e}")
            self._show_error_dialog(page, f"Error al iniciar: {e}")
    
    def _configure_page(self, page: ft.Page):
        """Configura las propiedades básicas de la página."""
        page.title = "Cámara IP Avanzada - v1.0.0"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.START
        
        # Configurar ventana (solo para desktop)
        if hasattr(page, 'window') and page.window:
            page.window.width = 1200
            page.window.height = 800
            page.window.min_width = 800
            page.window.min_height = 600
            page.window.center()
        
        # Configurar para móvil
        page.scroll = ft.ScrollMode.AUTO
        page.adaptive = True
        
        # Aplicar tema inicial
        self.theme_manager.apply_theme(page)
        
    def _setup_window_events(self, page: ft.Page):
        """Configura los eventos de la ventana."""
        def on_window_event(e):
            if e.data == "close":
                self._cleanup()
        
        page.on_window_event = on_window_event
        
    def _cleanup(self):
        """Limpia recursos al cerrar la aplicación."""
        try:
            if self.stream_manager:
                self.stream_manager.stop_all_streams()
            
            if self.network_discovery:
                self.network_discovery.stop()
                
            self.logger.info("Aplicación cerrada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error durante la limpieza: {e}")
    
    def _show_error_dialog(self, page: ft.Page, message: str):
        """Muestra un diálogo de error."""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: page.close(dialog))
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()


def main():
    """Función principal de entrada."""
    # Crear directorios necesarios
    Path("recordings").mkdir(exist_ok=True)
    Path("photos").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Crear y ejecutar la aplicación
    app = IPCameraApp()
    
    try:
        ft.app(target=app.run, assets_dir="assets")
    except Exception as e:
        print(f"Error crítico al iniciar la aplicación: {e}")
        logging.error(f"Error crítico: {e}")


if __name__ == "__main__":
    main()