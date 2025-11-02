#!/bin/bash

# Script de entrada para el contenedor Docker

set -e

# Función para ejecutar la app web móvil
run_web() {
    echo "🚀 Iniciando IP Camera Mobile Web App..."
    echo "📱 Acceso web disponible en puerto 8080"
    exec python mobile_web.py
}

# Función para ejecutar el receptor desktop
run_desktop() {
    echo "🖥️ Iniciando Desktop Receiver..."
    echo "📡 Receptor HTTP disponible en puerto 8081" 
    exec python desktop_receiver.py
}

# Función para ejecutar el launcher
run_launcher() {
    echo "🚀 Iniciando Launcher Interactivo..."
    exec python start.py
}

# Función para ejecutar tests
run_tests() {
    echo "🧪 Ejecutando tests del sistema..."
    exec python test_system.py
}

# Función de ayuda
show_help() {
    echo "IP Camera Mobile Web System - Docker Container"
    echo ""
    echo "Uso: docker run [opciones] imagen [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  web        - Ejecutar mobile web app (puerto 8080)"
    echo "  desktop    - Ejecutar desktop receiver (puerto 8081)"
    echo "  launcher   - Ejecutar launcher interactivo"
    echo "  tests      - Ejecutar suite de tests"
    echo "  help       - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  docker run -p 8080:8080 ipwebmobile web"
    echo "  docker run -p 8081:8081 ipwebmobile desktop"
    echo "  docker run -p 8080:8080 -p 8081:8081 ipwebmobile launcher"
}

# Procesar argumentos
case "$1" in
    web)
        run_web
        ;;
    desktop)
        run_desktop
        ;;
    launcher)
        run_launcher
        ;;
    tests)
        run_tests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "⚠️ Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac