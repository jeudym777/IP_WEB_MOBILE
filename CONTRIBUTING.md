# Guía de Desarrollo

Esta guía está dirigida a desarrolladores que deseen contribuir o extender la funcionalidad de la aplicación de Cámara IP Avanzada.

## 🏗️ Arquitectura del Proyecto

### Estructura de Directorios

```
APP_WEBIPMOBIL/
├── src/                    # Código fuente principal
│   ├── ui/                 # Componentes de interfaz de usuario
│   │   ├── components/     # Componentes reutilizables
│   │   └── main_window.py  # Ventana principal
│   ├── camera/             # Gestión de cámaras y streams
│   │   └── stream_manager.py
│   ├── network/            # Descubrimiento y comunicación
│   │   └── discovery.py
│   └── utils/              # Utilidades y configuración
│       ├── config_manager.py
│       ├── helpers.py
│       └── logger.py
├── assets/                 # Recursos estáticos
├── recordings/             # Videos grabados
├── photos/                 # Fotos capturadas
└── main.py                # Punto de entrada
```

### Componentes Principales

#### 1. StreamManager (`src/camera/stream_manager.py`)
- **Propósito**: Gestiona múltiples streams de cámara
- **Características clave**:
  - Manejo de threads para cada stream
  - Grabación de video con OpenCV
  - Captura de fotos
  - Control de FPS y calidad

#### 2. NetworkDiscovery (`src/network/discovery.py`)
- **Propósito**: Descubrimiento automático de cámaras IP
- **Características clave**:
  - Escaneo paralelo de redes
  - Detección de servicios de cámara
  - Soporte para múltiples protocolos

#### 3. MainWindow (`src/ui/main_window.py`)
- **Propósito**: Interfaz principal de la aplicación
- **Características clave**:
  - Interfaz responsiva con Flet
  - Gestión de eventos de usuario
  - Integración con todos los servicios

## 🔧 Configuración del Entorno de Desarrollo

### Prerrequisitos

1. **Python 3.8+**
2. **Git**
3. **VS Code** (recomendado)

### Configuración Inicial

```bash
# Clonar el repositorio
git clone <repository_url>
cd APP_WEBIPMOBIL

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Extensiones VS Code Recomendadas

- Python
- Pylance
- Python Debugger
- GitLens

## 🚀 Ejecutando la Aplicación

### Modo Desarrollo
```bash
python main.py
```

### Modo Debug
```bash
python -m debugpy --listen 5678 --wait-for-client main.py
```

## 🧪 Testing

### Estructura de Tests
```
tests/
├── unit/                   # Tests unitarios
├── integration/            # Tests de integración
└── fixtures/               # Datos de prueba
```

### Ejecutar Tests
```bash
# Tests unitarios
python -m pytest tests/unit/

# Tests de integración
python -m pytest tests/integration/

# Cobertura
python -m pytest --cov=src tests/
```

## 📝 Convenciones de Código

### Estilo
- **PEP 8**: Seguir las convenciones de estilo de Python
- **Docstrings**: Documentar todas las funciones y clases
- **Type Hints**: Usar anotaciones de tipo cuando sea posible

### Ejemplo de Función
```python
def process_frame(self, frame: np.ndarray, quality: float = 1.0) -> Optional[bytes]:
    """
    Procesa un frame de video aplicando configuraciones de calidad.
    
    Args:
        frame: Frame de video como array de numpy
        quality: Factor de calidad (0.1 - 1.0)
        
    Returns:
        Frame procesado como bytes, o None si falla
        
    Raises:
        ValueError: Si la calidad está fuera del rango válido
    """
    if not 0.1 <= quality <= 1.0:
        raise ValueError("Quality must be between 0.1 and 1.0")
    
    # Implementación...
    return processed_bytes
```

## 🔌 Extendiendo Funcionalidad

### Agregando Nuevos Protocolos de Cámara

1. **Crear nueva clase** en `src/camera/protocols/`
2. **Heredar de BaseProtocol**:
```python
from src.camera.protocols.base import BaseProtocol

class RTSPProtocol(BaseProtocol):
    def connect(self, url: str) -> bool:
        # Implementar conexión RTSP
        pass
    
    def get_frame(self) -> Optional[np.ndarray]:
        # Implementar captura de frame
        pass
```

3. **Registrar protocolo** en `StreamManager`

### Agregando Nuevos Componentes UI

1. **Crear componente** en `src/ui/components/`
2. **Seguir patrón de Flet**:
```python
import flet as ft

class CustomWidget(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
    
    def build(self):
        return ft.Container(
            # Definir estructura
        )
```

## 🐛 Debugging

### Logs
- Los logs se guardan en `logs/app_YYYYMMDD.log`
- Niveles: DEBUG, INFO, WARNING, ERROR
- Configuración en `src/utils/logger.py`

### Debugging Común

#### Problemas de Stream
```python
# Agregar logging detallado
self.logger.debug(f"Attempting connection to {url}")
self.logger.debug(f"Frame shape: {frame.shape}")
```

#### Problemas de UI
```python
# Verificar estado de controles
print(f"Button enabled: {self.connect_button.disabled}")
```

## 📦 Empaquetado y Distribución

### Crear Executable
```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear executable
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

### Crear Instalador (Windows)
1. Usar NSIS o Inno Setup
2. Incluir dependencias de sistema (VC++ Redistributable)
3. Configurar asociaciones de archivo

## 🤝 Contribuyendo

### Proceso de Pull Request

1. **Fork del repositorio**
2. **Crear rama feature**:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Hacer cambios y commits**
4. **Ejecutar tests**
5. **Enviar pull request**

### Criterios de Aceptación
- [ ] Código sigue las convenciones establecidas
- [ ] Tests pasan satisfactoriamente
- [ ] Documentación actualizada
- [ ] No rompe funcionalidad existente

## 📚 Recursos Adicionales

- [Documentación de Flet](https://flet.dev/docs/)
- [OpenCV Python Tutorials](https://opencv-python-tutroials.readthedocs.io/)
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [IP Camera Protocols](https://en.wikipedia.org/wiki/IP_camera)

## 🆘 Soporte

Para reportar bugs o solicitar funcionalidades:
1. Abrir issue en GitHub
2. Incluir logs relevantes
3. Describir pasos para reproducir
4. Especificar entorno (OS, Python version, etc.)