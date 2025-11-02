#!/bin/bash

# 🌐 Cloudflare Deployment Script para IP Web Mobile
# Deploy completo en Cloudflare Pages + Workers

set -e

echo "🌐 IP Camera Mobile Web - Cloudflare Deploy"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo ""
    echo "Uso: ./cloudflare-deploy.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  pages      - Deploy a Cloudflare Pages"
    echo "  worker     - Deploy Cloudflare Worker"
    echo "  both       - Deploy Pages + Worker"
    echo "  build      - Solo build para Pages"
    echo "  dev        - Desarrollo local"
    echo "  setup      - Configuración inicial"
    echo ""
    echo "Ejemplos:"
    echo "  ./cloudflare-deploy.sh pages"
    echo "  ./cloudflare-deploy.sh both"
    echo "  ./cloudflare-deploy.sh setup"
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}📋 Verificando dependencias...${NC}"
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no está instalado${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python 3: $(python3 --version)${NC}"
    
    # Verificar Node.js (para Wrangler)
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}⚠️ Node.js no encontrado, instalando...${NC}"
        # En sistemas con package manager, instalar Node.js
        echo "💡 Instala Node.js desde: https://nodejs.org/"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
    
    # Verificar o instalar Wrangler
    if ! command -v wrangler &> /dev/null; then
        echo -e "${YELLOW}📦 Instalando Wrangler CLI...${NC}"
        npm install -g wrangler
    fi
    echo -e "${GREEN}✅ Wrangler CLI instalado${NC}"
}

# Función para configuración inicial
setup_cloudflare() {
    echo -e "${BLUE}🔧 Configuración inicial de Cloudflare...${NC}"
    
    # Login a Cloudflare
    echo -e "${YELLOW}🔐 Iniciando sesión en Cloudflare...${NC}"
    wrangler login
    
    # Verificar autenticación
    if wrangler whoami &> /dev/null; then
        echo -e "${GREEN}✅ Autenticado correctamente${NC}"
    else
        echo -e "${RED}❌ Error de autenticación${NC}"
        exit 1
    fi
    
    # Crear configuraciones si no existen
    if [ ! -f "wrangler.toml" ]; then
        echo -e "${YELLOW}📝 Creando configuración wrangler.toml...${NC}"
        echo "name = \"ip-web-mobile\"" > wrangler.toml
        echo "main = \"worker.js\"" >> wrangler.toml
        echo "compatibility_date = \"$(date +%Y-%m-%d)\"" >> wrangler.toml
    fi
    
    echo -e "${GREEN}✅ Configuración completada${NC}"
}

# Función para build de Pages
build_pages() {
    echo -e "${BLUE}🏗️ Building para Cloudflare Pages...${NC}"
    
    # Ejecutar build script
    python3 build_for_pages.py
    
    if [ -d "dist" ]; then
        echo -e "${GREEN}✅ Build completado - archivos en /dist${NC}"
        echo "📁 Archivos generados:"
        ls -la dist/
    else
        echo -e "${RED}❌ Error en build - directorio /dist no encontrado${NC}"
        exit 1
    fi
}

# Función para deploy de Pages
deploy_pages() {
    echo -e "${BLUE}📱 Deployando a Cloudflare Pages...${NC}"
    
    # Build primero
    build_pages
    
    # Deploy usando Wrangler
    echo -e "${YELLOW}🚀 Iniciando deployment...${NC}"
    
    if wrangler pages deploy dist --project-name ip-web-mobile; then
        echo -e "${GREEN}✅ Pages deployado exitosamente!${NC}"
        echo -e "${GREEN}🌍 Tu app está disponible en: https://ip-web-mobile.pages.dev${NC}"
    else
        echo -e "${RED}❌ Error en deployment de Pages${NC}"
        exit 1
    fi
}

# Función para deploy de Worker
deploy_worker() {
    echo -e "${BLUE}⚡ Deployando Cloudflare Worker...${NC}"
    
    # Verificar que worker.js existe
    if [ ! -f "worker.js" ]; then
        echo -e "${RED}❌ worker.js no encontrado${NC}"
        exit 1
    fi
    
    # Deploy worker
    if wrangler deploy; then
        echo -e "${GREEN}✅ Worker deployado exitosamente!${NC}"
        echo -e "${GREEN}⚡ Worker disponible en: https://ip-web-mobile.tu-cuenta.workers.dev${NC}"
    else
        echo -e "${RED}❌ Error en deployment de Worker${NC}"
        exit 1
    fi
}

# Función para deploy completo
deploy_both() {
    echo -e "${BLUE}🚀 Deploy completo: Pages + Worker${NC}"
    
    # Deploy Worker primero
    deploy_worker
    
    echo ""
    
    # Deploy Pages después
    deploy_pages
    
    echo ""
    echo -e "${GREEN}🎉 ¡Deployment completo exitoso!${NC}"
    echo -e "${GREEN}📱 Pages: https://ip-web-mobile.pages.dev${NC}"
    echo -e "${GREEN}⚡ Worker: https://ip-web-mobile.tu-cuenta.workers.dev${NC}"
}

# Función para desarrollo local
dev_mode() {
    echo -e "${BLUE}💻 Iniciando modo desarrollo...${NC}"
    
    # Ejecutar en paralelo Pages dev y Worker dev
    echo -e "${YELLOW}🔧 Iniciando desarrollo local...${NC}"
    
    # Build primero
    build_pages
    
    # Iniciar dev server
    echo -e "${BLUE}📱 Servidor local en: http://localhost:8788${NC}"
    wrangler pages dev dist --port 8788 &
    
    # Iniciar worker dev
    echo -e "${BLUE}⚡ Worker dev en: http://localhost:8787${NC}"
    wrangler dev --port 8787
}

# Función para obtener información del deployment
get_info() {
    echo -e "${BLUE}📊 Información del deployment...${NC}"
    
    echo -e "${YELLOW}🏢 Cuenta Cloudflare:${NC}"
    wrangler whoami
    
    echo -e "${YELLOW}📱 Pages deployments:${NC}"
    wrangler pages deployment list --project-name ip-web-mobile || echo "No hay deployments de Pages"
    
    echo -e "${YELLOW}⚡ Workers:${NC}"
    wrangler list || echo "No hay Workers deployados"
}

# Función principal
main() {
    case "$1" in
        setup)
            check_dependencies
            setup_cloudflare
            ;;
        build)
            build_pages
            ;;
        pages)
            check_dependencies
            deploy_pages
            ;;
        worker)
            check_dependencies
            deploy_worker
            ;;
        both)
            check_dependencies
            deploy_both
            ;;
        dev)
            check_dependencies
            dev_mode
            ;;
        info)
            get_info
            ;;
        help|--help|-h|"")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Comando desconocido: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Banner inicial
echo -e "${BLUE}"
cat << "EOF"
   _____ _                 _  __ _                
  / ____| |               | |/ _| |               
 | |    | | ___  _   _  __| | |_| | __ _ _ __ ___  
 | |    | |/ _ \| | | |/ _` |  _| |/ _` | '__/ _ \ 
 | |____| | (_) | |_| | (_| | | | | (_| | | |  __/ 
  \_____|_|\___/ \__,_|\__,_|_| |_|\__,_|_|  \___| 
                                                  
              IP Camera Mobile Web                
EOF
echo -e "${NC}"

# Ejecutar función principal
main "$@"