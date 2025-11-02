#!/bin/bash

# 🚀 Deploy Script para IP Web Mobile
# Este script automatiza el deployment en diferentes plataformas

set -e

echo "🚀 IP Camera Mobile Web System - Deploy Script"
echo "=============================================="

# Función para mostrar ayuda
show_help() {
    echo ""
    echo "Uso: ./deploy.sh [plataforma]"
    echo ""
    echo "Plataformas soportadas:"
    echo "  railway    - Deploy a Railway.app"
    echo "  vercel     - Deploy a Vercel" 
    echo "  heroku     - Deploy a Heroku"
    echo "  docker     - Build Docker image"
    echo "  local      - Test local"
    echo ""
    echo "Ejemplos:"
    echo "  ./deploy.sh railway"
    echo "  ./deploy.sh docker"
    echo "  ./deploy.sh local"
}

# Función para preparar archivos
prepare_files() {
    echo "📋 Preparando archivos para deployment..."
    
    # Verificar que requirements.txt existe
    if [ ! -f "requirements.txt" ]; then
        echo "❌ requirements.txt no encontrado"
        exit 1
    fi
    
    # Verificar archivos principales
    if [ ! -f "mobile_web.py" ]; then
        echo "❌ mobile_web.py no encontrado"
        exit 1
    fi
    
    echo "✅ Archivos verificados"
}

# Deploy a Railway
deploy_railway() {
    echo "🚂 Deployando a Railway.app..."
    
    # Verificar Railway CLI
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI no instalado"
        echo "💡 Instalar con: npm install -g @railway/cli"
        exit 1
    fi
    
    # Login y deploy
    echo "🔐 Iniciando sesión en Railway..."
    railway login
    
    echo "🚀 Iniciando deployment..."
    railway up
    
    echo "✅ Deploy a Railway completado!"
    echo "🌍 Tu app estará disponible en el dashboard de Railway"
}

# Deploy a Vercel
deploy_vercel() {
    echo "▲ Deployando a Vercel..."
    
    # Verificar Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI no instalado"
        echo "💡 Instalar con: npm install -g vercel"
        exit 1
    fi
    
    # Deploy
    echo "🚀 Iniciando deployment..."
    vercel --prod
    
    echo "✅ Deploy a Vercel completado!"
}

# Deploy a Heroku
deploy_heroku() {
    echo "🟪 Deployando a Heroku..."
    
    # Verificar Heroku CLI
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI no instalado"
        echo "💡 Instalar desde: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Crear app si no existe
    echo "📱 Creando aplicación Heroku..."
    heroku create ip-web-mobile-$(date +%s) || true
    
    # Configurar buildpacks
    echo "🔧 Configurando buildpacks..."
    heroku buildpacks:add heroku/python
    
    # Deploy
    echo "🚀 Iniciando deployment..."
    git push heroku master
    
    echo "✅ Deploy a Heroku completado!"
}

# Build Docker image
build_docker() {
    echo "🐳 Construyendo imagen Docker..."
    
    # Build image
    docker build -t ip-web-mobile:latest .
    
    echo "✅ Imagen Docker construida!"
    echo "🚀 Ejecutar con: docker run -p 8080:8080 ip-web-mobile:latest"
}

# Test local
test_local() {
    echo "💻 Ejecutando test local..."
    
    # Instalar dependencias
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
    
    # Ejecutar tests
    echo "🧪 Ejecutando tests..."
    python test_system.py
    
    # Ejecutar app
    echo "🚀 Iniciando aplicación local..."
    echo "📱 Abre http://localhost:8080 en tu navegador"
    python mobile_web.py
}

# Función principal
main() {
    case "$1" in
        railway)
            prepare_files
            deploy_railway
            ;;
        vercel)
            prepare_files
            deploy_vercel
            ;;
        heroku)
            prepare_files
            deploy_heroku
            ;;
        docker)
            prepare_files
            build_docker
            ;;
        local)
            test_local
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo "❌ Plataforma desconocida: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"