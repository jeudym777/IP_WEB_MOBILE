"""
Utilidades varias para la aplicación de cámara IP.
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse


def validate_ip_address(ip: str) -> bool:
    """
    Valida si una cadena es una dirección IP válida.
    
    Args:
        ip: Dirección IP a validar
        
    Returns:
        True si es válida, False en caso contrario
    """
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def parse_ip_port(ip_port: str) -> Optional[Tuple[str, int]]:
    """
    Parsea una cadena IP:PUERTO.
    
    Args:
        ip_port: Cadena en formato IP:PUERTO
        
    Returns:
        Tupla (IP, PUERTO) o None si es inválida
    """
    try:
        if ':' not in ip_port:
            return None
            
        ip, port_str = ip_port.split(':', 1)
        port = int(port_str)
        
        if not validate_ip_address(ip):
            return None
            
        if not (1 <= port <= 65535):
            return None
            
        return (ip, port)
        
    except (ValueError, AttributeError):
        return None


def build_stream_url(ip_port: str, scheme: str = "http", path: str = "/video") -> str:
    """
    Construye una URL completa para el stream de la cámara.
    
    Args:
        ip_port: IP:PUERTO de la cámara
        scheme: Esquema de la URL (http/https)
        path: Ruta del stream
        
    Returns:
        URL completa del stream
    """
    ip_port = ip_port.strip()
    if not ip_port:
        return ""
        
    if ip_port.startswith("http://") or ip_port.startswith("https://"):
        base = ip_port.rstrip("/")
    else:
        base = f"{scheme}://{ip_port}"
        
    if not path.startswith("/"):
        path = "/" + path
        
    return f"{base}{path}"


def format_bytes(bytes_count: int) -> str:
    """
    Formatea un número de bytes en una cadena legible.
    
    Args:
        bytes_count: Número de bytes
        
    Returns:
        Cadena formateada (ej: "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Formatea una duración en segundos a formato HH:MM:SS.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        Cadena formateada (ej: "01:23:45")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def is_valid_url(url: str) -> bool:
    """
    Valida si una URL es válida.
    
    Args:
        url: URL a validar
        
    Returns:
        True si es válida, False en caso contrario
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False