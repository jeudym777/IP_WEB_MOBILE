# 📱 Sistema de Cámara IP Móvil

## 🎯 ¿Qué hace esta aplicación?

Este sistema te permite **usar tu celular como cámara IP** y ver la transmisión en tiempo real en tu computadora desktop. Es perfecto para:

- 🏠 Monitoreo casero
- 👶 Vigilancia de bebés  
- 🎥 Transmisiones en vivo
- 📹 Grabación remota
- 🔍 Cámaras de seguridad improvisadas

## 🚀 Inicio Rápido

### Método 1: Script Automático (Recomendado)
1. Haz doble clic en `inicio.bat`
2. Sigue las instrucciones en pantalla

### Método 2: Manual

**Paso 1: Iniciar receptor en PC**
```bash
python desktop_receiver.py
```

**Paso 2: Abrir app en celular**
```bash
python mobile_web.py
```
Luego ve a `http://[IP_DE_TU_PC]:8080` en tu celular.

## 📋 Requisitos

### ✅ Lo que necesitas:
- **PC con Windows** (donde se ejecuta el código)
- **Celular con navegador web** (Chrome, Firefox, Safari)
- **Misma red WiFi** para ambos dispositivos
- **Permisos de cámara** en el navegador del celular

### 🔧 Dependencias (ya instaladas):
- Python 3.8+
- Flet
- OpenCV
- NumPy

## 📱 Cómo usar desde el celular

### 1. Preparar la PC
1. Ejecuta `desktop_receiver.py` en tu PC
2. Aparecerá una ventana mostrando la IP del servidor
3. Anota esa IP (ejemplo: `192.168.1.100`)

### 2. Conectar el celular
1. En tu celular, abre el navegador
2. Ve a: `http://[IP_DE_TU_PC]:8080`
3. Verás la interfaz de la cámara móvil

### 3. Iniciar transmisión
1. Ingresa la IP de tu PC en el campo correspondiente
2. Presiona **"📹 Iniciar Cámara"**
3. Permite acceso a la cámara cuando el navegador lo solicite
4. ¡El video aparecerá inmediatamente en tu PC!

## 🎮 Controles disponibles

### 📱 En el celular:
- **📹 Iniciar Cámara**: Comienza la transmisión
- **⏹️ Detener**: Para la transmisión
- **Campo IP**: Configura la IP de destino

### 🖥️ En la PC:
- **🚀 Iniciar Servidor**: Activa el receptor
- **⏹️ Detener Servidor**: Desactiva el receptor
- **🔴 Grabar**: Graba el video recibido
- **📸 Foto**: Captura una imagen

## 🔧 Configuración de red

### Encontrar tu IP:
**Windows:**
```cmd
ipconfig
```
Busca la línea que dice "IPv4" (ejemplo: `192.168.1.100`)

**Verificar conectividad:**
Ambos dispositivos deben poder hacer `ping` entre sí.

## 📂 Archivos generados

### 📹 Videos grabados:
- Ubicación: `recordings/`
- Formato: `mobile_stream_YYYYMMDD_HHMMSS.mp4`
- Calidad: 640x480 a 15 FPS

### 📸 Fotos capturadas:
- Ubicación: `photos/`
- Formato: `mobile_photo_YYYYMMDD_HHMMSS.jpg`
- Resolución: Según la cámara del celular

## 🐛 Solución de problemas

### ❌ "No se puede acceder a la cámara"
- **Causa**: Permisos del navegador
- **Solución**: Permite acceso a la cámara en la configuración del navegador

### ❌ "Error de conexión"
- **Causa**: IP incorrecta o firewall
- **Solución**: 
  1. Verifica que ambos dispositivos estén en la misma red
  2. Confirma la IP con `ipconfig`
  3. Desactiva temporalmente el firewall de Windows

### ❌ "No aparece video en PC"
- **Causa**: Servidor no iniciado o puerto bloqueado
- **Solución**:
  1. Asegúrate de ejecutar `desktop_receiver.py` primero
  2. Verifica que el puerto 8081 esté libre

### ❌ Video muy lento o entrecortado
- **Causa**: Red WiFi lenta
- **Solución**: Acércate al router WiFi o usa red 5GHz

## 🔒 Seguridad

### ⚠️ Importante:
- El sistema transmite **sin encriptación**
- Solo usar en redes WiFi **confiables**
- No usar en redes públicas
- El video solo se transmite en la red local

### 🛡️ Recomendaciones:
- Usar solo en tu red doméstica
- Cerrar las aplicaciones cuando no las uses
- No compartir la IP con extraños

## 🎯 Casos de uso prácticos

### 🏠 Monitor de bebé:
1. Deja el celular en la habitación del bebé
2. Ve el video desde tu PC en otra habitación
3. Graba momentos importantes

### 🎥 Transmisión de eventos:
1. Coloca el celular en el lugar del evento
2. Transmite en vivo a tu PC
3. Graba todo el evento

### 🔍 Cámara de seguridad:
1. Coloca el celular en un punto estratégico
2. Monitorea desde tu PC
3. Recibe alertas de movimiento (función futura)

## 📈 Características técnicas

### 📱 Aplicación móvil:
- **Framework**: Flet Web
- **Resolución**: Hasta 1080p (según celular)
- **FPS**: 10-15 fps
- **Compresión**: JPEG con calidad 80%
- **Latencia**: < 500ms en red local

### 🖥️ Aplicación desktop:
- **Framework**: Flet Desktop
- **Protocolo**: HTTP POST
- **Puerto**: 8081
- **Formato grabación**: MP4 (H.264)
- **Almacenamiento**: Local

## 🛠️ Desarrollo futuro

### 🔜 Próximas características:
- [ ] Detección de movimiento
- [ ] Múltiples cámaras simultáneas
- [ ] Notificaciones push
- [ ] Transmisión RTSP
- [ ] Control de zoom/enfoque
- [ ] Modo nocturno
- [ ] Grabación en la nube

### 🤝 Contribuir:
¿Tienes ideas o mejoras? ¡Envía un pull request!

## 📞 Soporte

### 🆘 ¿Necesitas ayuda?
1. Revisa la sección de **Solución de problemas**
2. Verifica que cumples todos los **Requisitos**
3. Consulta los **logs** en la consola
4. Abre un **issue** en GitHub

---

## 🎉 ¡Disfruta tu nueva cámara IP móvil!

Ahora puedes convertir cualquier celular en una cámara IP profesional y ver todo desde tu PC. ¡Las posibilidades son infinitas! 📱➡️🖥️