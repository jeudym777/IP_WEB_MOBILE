@echo off
REM 🌐 Cloudflare Deployment Script para Windows
REM Deploy completo en Cloudflare Pages + Workers

setlocal enabledelayedexpansion

echo 🌐 IP Camera Mobile Web - Cloudflare Deploy
echo ==========================================

if "%1"=="setup" goto setup
if "%1"=="build" goto build
if "%1"=="pages" goto pages
if "%1"=="worker" goto worker
if "%1"=="both" goto both
if "%1"=="dev" goto dev
if "%1"=="info" goto info
if "%1"=="help" goto help
if "%1"=="" goto help

echo ❌ Comando desconocido: %1
goto help

:help
echo.
echo Uso: cloudflare-deploy.bat [comando]
echo.
echo Comandos disponibles:
echo   setup      - Configuración inicial
echo   build      - Solo build para Pages
echo   pages      - Deploy a Cloudflare Pages
echo   worker     - Deploy Cloudflare Worker
echo   both       - Deploy Pages + Worker
echo   dev        - Desarrollo local
echo   info       - Información del deployment
echo.
echo Ejemplos:
echo   cloudflare-deploy.bat setup
echo   cloudflare-deploy.bat both
echo   cloudflare-deploy.bat pages
goto end

:setup
echo 🔧 Configuración inicial de Cloudflare...

REM Verificar Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado
    echo 💡 Descarga desde: https://nodejs.org/
    exit /b 1
)
echo ✅ Node.js encontrado

REM Verificar/Instalar Wrangler
where wrangler >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 Instalando Wrangler CLI...
    npm install -g wrangler
    if %errorlevel% neq 0 (
        echo ❌ Error instalando Wrangler
        exit /b 1
    )
)
echo ✅ Wrangler CLI disponible

REM Login a Cloudflare
echo 🔐 Iniciando sesión en Cloudflare...
wrangler login
if %errorlevel% neq 0 (
    echo ❌ Error en login de Cloudflare
    exit /b 1
)

echo ✅ Configuración completada
goto end

:build
echo 🏗️ Building para Cloudflare Pages...

python build_for_pages.py
if %errorlevel% neq 0 (
    echo ❌ Error en build
    exit /b 1
)

if exist "dist" (
    echo ✅ Build completado - archivos en /dist
    dir dist
) else (
    echo ❌ Error: directorio dist no encontrado
    exit /b 1
)
goto end

:pages
echo 📱 Deployando a Cloudflare Pages...

REM Build primero
call :build
if %errorlevel% neq 0 exit /b 1

REM Deploy Pages
echo 🚀 Iniciando deployment...
wrangler pages deploy dist --project-name ip-web-mobile
if %errorlevel% neq 0 (
    echo ❌ Error en deployment de Pages
    exit /b 1
)

echo ✅ Pages deployado exitosamente!
echo 🌍 Tu app está disponible en: https://ip-web-mobile.pages.dev
goto end

:worker
echo ⚡ Deployando Cloudflare Worker...

REM Verificar worker.js
if not exist "worker.js" (
    echo ❌ worker.js no encontrado
    exit /b 1
)

REM Deploy worker
wrangler deploy
if %errorlevel% neq 0 (
    echo ❌ Error en deployment de Worker
    exit /b 1
)

echo ✅ Worker deployado exitosamente!
echo ⚡ Worker disponible
goto end

:both
echo 🚀 Deploy completo: Pages + Worker

REM Deploy Worker primero
call :worker
if %errorlevel% neq 0 exit /b 1

echo.
REM Deploy Pages después
call :pages
if %errorlevel% neq 0 exit /b 1

echo.
echo 🎉 ¡Deployment completo exitoso!
echo 📱 Pages: https://ip-web-mobile.pages.dev
echo ⚡ Worker deployado correctamente
goto end

:dev
echo 💻 Iniciando modo desarrollo...

REM Build primero
call :build
if %errorlevel% neq 0 exit /b 1

echo 📱 Iniciando servidor de desarrollo...
echo 🌍 Servidor local en: http://localhost:8788
wrangler pages dev dist --port 8788
goto end

:info
echo 📊 Información del deployment...

echo 🏢 Cuenta Cloudflare:
wrangler whoami

echo.
echo 📱 Pages deployments:
wrangler pages deployment list --project-name ip-web-mobile 2>nul || echo No hay deployments de Pages

echo.
echo ⚡ Workers:
wrangler list 2>nul || echo No hay Workers deployados
goto end

:end
pause