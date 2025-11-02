# Comandos para generar APK

## Instalar herramientas de build
pip install flet[build]

## Generar APK (requiere Android SDK configurado)
flet build apk

## Generar APK con configuración personalizada
flet build apk --build-number 1 --build-version 1.0.0

## Para desarrollo/testing (APK debug)
flet build apk --debug

## Requisitos del sistema para build Android:
# 1. Java JDK 8 o superior
# 2. Android SDK
# 3. Android NDK
# 4. Configurar variables de entorno:
#    - ANDROID_HOME
#    - JAVA_HOME

## Alternativa: Usar GitHub Actions o servicio cloud para build