"""
Módulo de descubrimiento automático de cámaras IP en la red.
"""

import socket
import threading
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from ipaddress import IPv4Network

# Importación opcional de netifaces
try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    netifaces = None
    HAS_NETIFACES = False


@dataclass
class CameraDevice:
    """Información de un dispositivo de cámara encontrado."""
    ip_address: str
    port: int
    name: str = ""
    manufacturer: str = ""
    model: str = ""
    mac_address: str = ""
    services: List[str] = None
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.services is None:
            self.services = []
    
    @property
    def url(self) -> str:
        """URL base del dispositivo."""
        return f"http://{self.ip_address}:{self.port}"


class NetworkScanner:
    """Escáner de red para encontrar dispositivos con cámaras."""
    
    def __init__(self):
        """Inicializa el escáner."""
        self.logger = logging.getLogger(__name__)
        
    def get_local_networks(self) -> List[str]:
        """
        Obtiene las redes locales disponibles.
        
        Returns:
            Lista de redes en formato CIDR
        """
        networks = []
        
        try:
            if HAS_NETIFACES:
                # Usar netifaces si está disponible
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    
                    # Solo IPv4
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info.get('addr')
                            netmask = addr_info.get('netmask')
                            
                            if ip and netmask and not ip.startswith('127.'):
                                try:
                                    # Calcular red
                                    network = IPv4Network(f"{ip}/{netmask}", strict=False)
                                    networks.append(str(network.network_address) + f"/{network.prefixlen}")
                                except Exception as e:
                                    self.logger.debug(f"Error procesando {ip}/{netmask}: {e}")
            else:
                # Fallback: obtener IP local usando socket
                try:
                    # Conectar a una IP externa para obtener la IP local
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    
                    # Asumir red /24 para la IP local
                    if local_ip.startswith('192.168.'):
                        base = '.'.join(local_ip.split('.')[:-1])
                        networks.append(f"{base}.0/24")
                    elif local_ip.startswith('10.'):
                        networks.append("10.0.0.0/24")
                    else:
                        networks.append("192.168.1.0/24")  # Fallback común
                        
                except Exception:
                    pass
                                
        except Exception as e:
            self.logger.error(f"Error obteniendo redes locales: {e}")
        
        # Si no se encontraron redes, usar valores por defecto
        if not networks:
            networks = ['192.168.1.0/24', '192.168.0.0/24', '10.0.0.0/24']
            
        return networks
    
    def scan_network(self, network: str, ports: List[int] = None, 
                    progress_callback: Optional[Callable[[int, int], None]] = None) -> List[CameraDevice]:
        """
        Escanea una red buscando dispositivos de cámara.
        
        Args:
            network: Red en formato CIDR (ej: 192.168.1.0/24)
            ports: Lista de puertos a escanear
            progress_callback: Callback para reportar progreso (actual, total)
            
        Returns:
            Lista de dispositivos encontrados
        """
        if ports is None:
            ports = [8080, 8081, 80, 443, 554, 8554, 9999]  # Puertos comunes para cámaras IP
            
        devices = []
        
        try:
            net = IPv4Network(network, strict=False)
            total_hosts = len(list(net.hosts()))
            
            if progress_callback:
                progress_callback(0, total_hosts)
            
            # Usar ThreadPoolExecutor para escaneo paralelo
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = []
                
                for i, host in enumerate(net.hosts()):
                    future = executor.submit(self._scan_host, str(host), ports)
                    futures.append((future, i + 1))
                
                # Recoger resultados
                for future, count in futures:
                    try:
                        device = future.result(timeout=5.0)
                        if device:
                            devices.append(device)
                            
                        if progress_callback:
                            progress_callback(count, total_hosts)
                            
                    except Exception as e:
                        self.logger.debug(f"Error en escaneo: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error escaneando red {network}: {e}")
            
        return devices
    
    def _scan_host(self, ip: str, ports: List[int]) -> Optional[CameraDevice]:
        """
        Escanea un host específico en busca de servicios de cámara.
        
        Args:
            ip: Dirección IP del host
            ports: Lista de puertos a probar
            
        Returns:
            Dispositivo de cámara si se encuentra, None en caso contrario
        """
        for port in ports:
            if self._check_camera_service(ip, port):
                device = CameraDevice(ip_address=ip, port=port)
                
                # Intentar obtener información adicional
                self._get_device_info(device)
                
                return device
                
        return None
    
    def _check_camera_service(self, ip: str, port: int) -> bool:
        """
        Verifica si hay un servicio de cámara en el host:puerto especificado.
        
        Args:
            ip: Dirección IP
            port: Puerto
            
        Returns:
            True si se detecta un servicio de cámara
        """
        try:
            # Primero verificar conectividad TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result != 0:
                return False
            
            # Verificar si es un servicio HTTP con posible cámara
            start_time = time.time()
            
            try:
                response = requests.get(f"http://{ip}:{port}", timeout=3.0, 
                                     allow_redirects=False)
                
                response_time = time.time() - start_time
                
                # Buscar indicadores de servicio de cámara
                indicators = [
                    'webcam', 'camera', 'mjpeg', 'video', 'stream',
                    'ip camera', 'surveillance', 'nvr', 'dvr'
                ]
                
                content = response.text.lower() if response.text else ""
                headers = str(response.headers).lower()
                
                for indicator in indicators:
                    if indicator in content or indicator in headers:
                        return True
                        
                # También verificar rutas comunes de cámara
                common_paths = ['/video', '/mjpeg', '/cam', '/stream']
                for path in common_paths:
                    try:
                        cam_response = requests.get(f"http://{ip}:{port}{path}", 
                                                  timeout=2.0, stream=True)
                        if cam_response.status_code == 200:
                            content_type = cam_response.headers.get('content-type', '')
                            if 'image' in content_type or 'video' in content_type:
                                return True
                    except:
                        continue
                        
            except requests.RequestException:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error verificando {ip}:{port}: {e}")
            
        return False
    
    def _get_device_info(self, device: CameraDevice) -> None:
        """
        Obtiene información adicional del dispositivo.
        
        Args:
            device: Dispositivo a investigar
        """
        try:
            start_time = time.time()
            response = requests.get(device.url, timeout=3.0)
            device.response_time = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Intentar extraer información del dispositivo
                if 'ip webcam' in content:
                    device.name = "IP Webcam (Android)"
                elif 'mjpeg streamer' in content:
                    device.name = "MJPEG Streamer"
                elif 'camera' in content:
                    device.name = "Cámara IP"
                else:
                    device.name = f"Dispositivo en {device.ip_address}"
                
                # Verificar servicios disponibles
                common_endpoints = [
                    '/video', '/mjpeg', '/snapshot', '/cam', 
                    '/stream', '/shot.jpg', '/videofeed'
                ]
                
                for endpoint in common_endpoints:
                    try:
                        test_response = requests.head(f"{device.url}{endpoint}", 
                                                    timeout=1.0)
                        if test_response.status_code == 200:
                            device.services.append(endpoint)
                    except:
                        continue
                        
        except Exception as e:
            self.logger.debug(f"Error obteniendo info de {device.ip_address}: {e}")
            device.name = f"Dispositivo en {device.ip_address}"


class NetworkDiscovery:
    """Servicio de descubrimiento automático de cámaras en red."""
    
    def __init__(self):
        """Inicializa el servicio de descubrimiento."""
        self.logger = logging.getLogger(__name__)
        self.scanner = NetworkScanner()
        self._is_scanning = False
        self._scan_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
    def start_scan(self, progress_callback: Optional[Callable[[int, int], None]] = None,
                  result_callback: Optional[Callable[[List[CameraDevice]], None]] = None) -> bool:
        """
        Inicia el escaneo automático de la red.
        
        Args:
            progress_callback: Callback para reportar progreso
            result_callback: Callback para recibir resultados
            
        Returns:
            True si el escaneo se inició correctamente
        """
        if self._is_scanning:
            return False
            
        self._stop_event.clear()
        
        def scan_worker():
            """Función del hilo de escaneo."""
            try:
                self._is_scanning = True
                all_devices = []
                
                networks = self.scanner.get_local_networks()
                self.logger.info(f"Escaneando redes: {networks}")
                
                for network in networks:
                    if self._stop_event.is_set():
                        break
                        
                    devices = self.scanner.scan_network(network, progress_callback=progress_callback)
                    all_devices.extend(devices)
                
                if result_callback and not self._stop_event.is_set():
                    result_callback(all_devices)
                    
                self.logger.info(f"Escaneo completado. Encontrados {len(all_devices)} dispositivos")
                
            except Exception as e:
                self.logger.error(f"Error durante el escaneo: {e}")
            finally:
                self._is_scanning = False
        
        self._scan_thread = threading.Thread(target=scan_worker, daemon=True)
        self._scan_thread.start()
        return True
    
    def stop(self) -> None:
        """Detiene el escaneo en curso."""
        self._stop_event.set()
        self._is_scanning = False
        
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join(timeout=2.0)
    
    def is_scanning(self) -> bool:
        """
        Verifica si hay un escaneo en curso.
        
        Returns:
            True si está escaneando
        """
        return self._is_scanning
    
    def quick_scan(self, target_ip: str = None) -> List[CameraDevice]:
        """
        Realiza un escaneo rápido de dispositivos conocidos.
        
        Args:
            target_ip: IP específica a escanear (opcional)
            
        Returns:
            Lista de dispositivos encontrados
        """
        devices = []
        
        if target_ip:
            # Escanear IP específica
            common_ports = [8080, 80, 8081]
            device = self.scanner._scan_host(target_ip, common_ports)
            if device:
                devices.append(device)
        else:
            # Escaneo rápido de IPs comunes
            common_ips = [
                '192.168.1.100', '192.168.1.101', '192.168.1.105',
                '192.168.0.100', '192.168.0.101', '192.168.0.105',
            ]
            
            for ip in common_ips:
                device = self.scanner._scan_host(ip, [8080])
                if device:
                    devices.append(device)
                    
        return devices