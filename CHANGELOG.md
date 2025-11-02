# Changelog

## v1.0.0 (2025-10-30)

### ✨ Características Iniciales
- **Visualización en tiempo real**: Stream de cámaras IP móviles
- **Grabación de video**: Grabación directa de transmisiones
- **Captura de fotos**: Toma de capturas instantáneas
- **Descubrimiento automático**: Búsqueda automática de cámaras en red local
- **Interfaz moderna**: UI construida con Flet
- **Temas personalizables**: Modo claro, oscuro y automático
- **Gestión de configuraciones**: Guardado automático de configuraciones
- **Historial de conexiones**: Recuerda conexiones previas

### 🏗️ Arquitectura
- Estructura modular separada por funcionalidades
- Gestión robusta de threads para streams
- Sistema de logging integrado
- Configuración persistente en JSON

### 📱 Compatibilidad
- Soporte para IP Webcam (Android)
- Múltiples formatos de stream (MJPEG, single frame)
- Detección automática de servicios de cámara

### 🔧 Tecnologías
- **Flet**: Interfaz de usuario moderna
- **OpenCV**: Procesamiento de video
- **Requests**: Comunicación HTTP
- **Threading**: Manejo concurrente de streams