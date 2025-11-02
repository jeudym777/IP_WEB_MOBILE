# 📱 IP Camera Mobile Web System

Una aplicación Python moderna construida con **Flet** que revoluciona la transmisión de cámaras IP permitiendo capturar video directamente desde navegadores móviles y transmitir en tiempo real a aplicaciones de escritorio.

## 🚀 Características Principales

### 📱 Sistema Web Móvil (NUEVO)
- **Captura Directa**: Accede a la cámara del móvil desde el navegador
- **Transmisión HTTP**: Sistema custom sin dependencias WebRTC complejas
- **Interfaz Responsive**: UI optimizada para dispositivos móviles
- **Zero Installation**: No requiere apps adicionales en el móvil

### 🖥️ Sistema Desktop Avanzado
- **📹 Transmisión en Tiempo Real**: Recibe streams desde múltiples fuentes
- **🎬 Grabación de Video**: Graba transmisiones en formato MP4
- **📸 Captura de Fotos**: Toma capturas instantáneas con timestamp
- **🔍 Descubrimiento de Red**: Encuentra automáticamente cámaras IP
- **🎨 Temas Personalizables**: Interfaz moderna con modo claro y oscuro
- **⚙️ Controles Remotos**: Control completo de funciones de cámara
- **📋 Gestión de Configuraciones**: Sistema de configuración persistente

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Windows 10/11
- Al menos 4GB de RAM
- Tarjeta de red compatible

## 🔧 Instalación

1. **Clona o descarga el proyecto**
2. **Instala las dependencias**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Ejecuta la aplicación**:
   ```powershell
   python main.py
   ```

## 📱 Configuración de la Cámara Móvil

### Para Android (IP Webcam):
1. Descarga "IP Webcam" desde Google Play Store
2. Abre la aplicación y configura la calidad deseada
3. Presiona "Iniciar servidor"
4. Anota la IP y puerto mostrados (ej: 192.168.1.105:8080)

### Para iOS (EpocCam/iVCam):
1. Instala una aplicación compatible como EpocCam o iVCam
2. Sigue las instrucciones específicas de la aplicación
3. Asegúrate de estar en la misma red Wi-Fi

## 🎯 Uso Rápido

### 🚀 Launcher Automático (Recomendado)
```bash
python start.py
```
Selecciona tu opción preferida del menú interactivo.

### 📱 Sistema Web Móvil (NUEVO)

1. **Ejecutar App Web**:
   ```bash
   python mobile_web.py
   ```

2. **Ejecutar Receptor Desktop** (en otra terminal):
   ```bash
   python desktop_receiver.py
   ```

3. **Conectar desde Móvil**:
   - Abre navegador en tu móvil
   - Navega a: `http://[IP_DE_TU_PC]:8080`
   - Introduce la IP del desktop
   - Presiona "📹 Iniciar Cámara"
   - ¡Permite acceso y listo!

### 💻 Sistema Desktop Tradicional
1. **Inicio**: Ejecuta `main.py`
2. **Conectar**: Ingresa la IP de tu cámara IP (ej: 192.168.1.105:8080)
3. **Visualizar**: Presiona "Conectar" para iniciar la transmisión
4. **Grabar**: Usa los controles para grabar video o tomar fotos

## 📁 Estructura del Proyecto

```
IP_WEB_MOBILE/
├── 📱 mobile_web.py           # App web para captura móvil (NUEVO)
├── 🖥️ desktop_receiver.py     # Receptor desktop con grabación (NUEVO)
├── 🚀 start.py               # Launcher interactivo (NUEVO)
├── 💻 main.py                # App desktop completa
├── 🧪 test_system.py         # Suite de tests automáticos
├── 📄 requirements.txt       # Dependencias Python
├── 📋 USAGE_GUIDE.md         # Guía detallada de uso
├── 📖 TECHNICAL_DOCUMENTATION.md  # Documentación técnica
├── src/                      # Código fuente modular
│   ├── ui/                   # Componentes de interfaz
│   ├── camera/               # Gestión de streams
│   ├── network/              # Descubrimiento de red
│   └── utils/                # Utilidades y configuración
├── recordings/               # Videos grabados (MP4)
├── photos/                   # Fotos capturadas (JPEG)
├── logs/                     # Archivos de log
└── assets/                   # Recursos e iconos
```

## 🛠️ Desarrollo

Para desarrolladores que quieran extender la aplicación:

1. **Arquitectura Modular**: Cada componente está separado en módulos específicos
2. **Extensible**: Fácil agregar nuevos protocolos de cámara
3. **Configurable**: Sistema de configuración flexible
4. **Documentado**: Código bien documentado para facilitar contribuciones

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crea una rama para tu característica
3. Confirma tus cambios
4. Envía un pull request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que tu cámara y PC estén en la misma red
2. Confirma que la aplicación de cámara esté ejecutándose
3. Revisa los logs en la consola para más información
4. Consulta la sección de problemas comunes

## 🔗 Enlaces Útiles

- [Documentación de Flet](https://flet.dev)
- [OpenCV Python](https://opencv-python-tutroials.readthedocs.io/)
- [IP Webcam para Android](https://play.google.com/store/apps/details?id=com.pas.webcam)

---

**¡Disfruta capturando momentos con tu cámara IP móvil!** 📸