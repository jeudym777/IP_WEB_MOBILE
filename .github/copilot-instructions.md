# Aplicación Avanzada de Cámara IP - Instrucciones para Copilot

Esta aplicación es una herramienta moderna construida con **Flet** para visualizar, controlar y grabar transmisiones de cámaras IP móviles.

## 🏗️ Arquitectura del Proyecto

- **Framework UI**: Flet (Python)
- **Procesamiento de Video**: OpenCV
- **Estructura**: Modular con separación clara de responsabilidades
- **Gestión de Estado**: Configuraciones persistentes en JSON

## 📁 Estructura de Módulos

- `src/ui/`: Componentes de interfaz de usuario y ventana principal
- `src/camera/`: Gestión de streams y grabación de video
- `src/network/`: Descubrimiento automático de dispositivos en red
- `src/utils/`: Utilidades, configuración y logging

## 🎯 Características Principales

- Visualización en tiempo real de múltiples cámaras IP
- Grabación de video con OpenCV
- Captura de fotos instantáneas
- Descubrimiento automático de dispositivos
- Temas personalizables (claro/oscuro)
- Gestión inteligente de configuraciones
- Soporte para IP Webcam (Android) y otros protocolos

## 🔧 Configuración de Desarrollo

- Python 3.8+ requerido
- Dependencias principales: flet, opencv-python, requests
- Entorno de desarrollo configurado para Windows
- Sistema de logging integrado en `logs/`

## 💡 Guías para Copilot

Cuando trabajes en este proyecto:

1. **Mantén la arquitectura modular** - Cada funcionalidad en su módulo correspondiente
2. **Usa type hints** - El código utiliza anotaciones de tipo consistentemente  
3. **Documentación detallada** - Todas las funciones tienen docstrings descriptivos
4. **Manejo de errores robusto** - Implementa try/catch apropiados con logging
5. **Threading consciente** - Los streams manejan concurrencia correctamente
6. **UI responsiva** - Usa invoke_later() para actualizaciones de UI desde threads

## 🎨 Patrones de Código

- Clases de configuración usando `@dataclass`
- Callbacks para comunicación entre componentes
- Gestión de recursos con context managers
- Logging estructurado con diferentes niveles

## 📱 Funcionalidades Específicas

- Protocolo HTTP/MJPEG para streams de cámara
- Detección automática de servicios en red local
- Grabación con control de FPS y calidad
- Sistema de temas con persistencia
- Historial de conexiones recientes