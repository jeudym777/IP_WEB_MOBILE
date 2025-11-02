"""
Gestor de configuraciones para la aplicación de cámara IP.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field


@dataclass
class CameraConfig:
    """Configuración de una cámara."""
    name: str
    ip_address: str
    port: int
    path: str = "/video"
    username: str = ""
    password: str = ""
    quality: str = "medium"
    auto_connect: bool = False
    
    @property
    def url(self) -> str:
        """Retorna la URL completa de la cámara."""
        return f"http://{self.ip_address}:{self.port}{self.path}"


@dataclass 
class AppSettings:
    """Configuraciones generales de la aplicación."""
    theme: str = "light"
    language: str = "es"
    auto_discovery: bool = True
    recording_quality: str = "high"
    photo_quality: str = "high"
    default_save_path: str = "recordings"
    recent_connections: List[str] = field(default_factory=list)
    window_width: int = 1200
    window_height: int = 800


class ConfigManager:
    """Gestor de configuraciones de la aplicación."""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa el gestor de configuraciones.
        
        Args:
            config_file: Nombre del archivo de configuración
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Configuraciones por defecto
        self.cameras: List[CameraConfig] = []
        self.settings = AppSettings()
        
        # Cargar configuraciones existentes
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Carga las configuraciones desde el archivo.
        
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            if not self.config_file.exists():
                self.logger.info("Archivo de configuración no encontrado, usando valores por defecto")
                self.save_config()
                return True
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar configuraciones de cámaras
            self.cameras = []
            for camera_data in data.get('cameras', []):
                self.cameras.append(CameraConfig(**camera_data))
            
            # Cargar configuraciones de la aplicación
            settings_data = data.get('settings', {})
            self.settings = AppSettings(**settings_data)
            
            self.logger.info("Configuraciones cargadas correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar configuraciones: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Guarda las configuraciones en el archivo.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            data = {
                'cameras': [asdict(camera) for camera in self.cameras],
                'settings': asdict(self.settings)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuraciones guardadas correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar configuraciones: {e}")
            return False
    
    def add_camera(self, camera: CameraConfig) -> None:
        """
        Añade una nueva configuración de cámara.
        
        Args:
            camera: Configuración de la cámara
        """
        self.cameras.append(camera)
        self.save_config()
    
    def remove_camera(self, name: str) -> bool:
        """
        Elimina una configuración de cámara.
        
        Args:
            name: Nombre de la cámara
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        for i, camera in enumerate(self.cameras):
            if camera.name == name:
                del self.cameras[i]
                self.save_config()
                return True
        return False
    
    def get_camera(self, name: str) -> Optional[CameraConfig]:
        """
        Obtiene una configuración de cámara por nombre.
        
        Args:
            name: Nombre de la cámara
            
        Returns:
            Configuración de la cámara o None si no existe
        """
        for camera in self.cameras:
            if camera.name == name:
                return camera
        return None
    
    def update_settings(self, **kwargs) -> None:
        """
        Actualiza las configuraciones de la aplicación.
        
        Args:
            **kwargs: Configuraciones a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save_config()
    
    def add_recent_connection(self, connection: str) -> None:
        """
        Añade una conexión reciente.
        
        Args:
            connection: String de conexión (IP:PUERTO)
        """
        if connection in self.settings.recent_connections:
            self.settings.recent_connections.remove(connection)
        
        self.settings.recent_connections.insert(0, connection)
        
        # Mantener solo las últimas 10 conexiones
        if len(self.settings.recent_connections) > 10:
            self.settings.recent_connections = self.settings.recent_connections[:10]
        
        self.save_config()