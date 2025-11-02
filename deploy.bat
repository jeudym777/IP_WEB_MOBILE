@echo off
REM 🚀 Deploy Script para IP Web Mobile - Windows Version

echo 🚀 IP Camera Mobile Web System - Deploy Script
echo ==============================================

if "%1"=="railway" goto railway
if "%1"=="vercel" goto vercel  
if "%1"=="heroku" goto heroku
if "%1"=="docker" goto docker
if "%1"=="local" goto local
if "%1"=="help" goto help
if "%1"=="" goto help

echo ❌ Plataforma desconocida: %1
goto help

:help
echo.
echo Uso: deploy.bat [plataforma]
echo.
echo Plataformas soportadas:
echo   railway    - Deploy a Railway.app
echo   vercel     - Deploy a Vercel
echo   heroku     - Deploy a Heroku  
echo   docker     - Build Docker image
echo   local      - Test local
echo.
echo Ejemplos:
echo   deploy.bat railway
echo   deploy.bat docker
echo   deploy.bat local
goto end

:railway
echo 🚂 Deployando a Railway.app...
echo 📋 Preparando archivos...

REM Verificar archivos
if not exist "requirements.txt" (
    echo ❌ requirements.txt no encontrado
    exit /b 1
)
if not exist "mobile_web.py" (
    echo ❌ mobile_web.py no encontrado  
    exit /b 1
)

echo ✅ Archivos verificados
echo 💡 Continúa el deployment en Railway dashboard
echo 🌍 URL: https://railway.app/new
echo 📁 Repositorio: https://github.com/jeudym777/IP_WEB_MOBILE
goto end

:vercel
echo ▲ Deployando a Vercel...
echo 💡 Usa Vercel CLI o dashboard web
echo 🌍 URL: https://vercel.com/new
echo 📁 Repositorio: https://github.com/jeudym777/IP_WEB_MOBILE
goto end

:heroku
echo 🟪 Deployando a Heroku...
echo 💡 Usa Heroku CLI o dashboard web  
echo 🌍 URL: https://dashboard.heroku.com/new-app
echo 📁 Repositorio: https://github.com/jeudym777/IP_WEB_MOBILE
goto end

:docker
echo 🐳 Construyendo imagen Docker...
docker build -t ip-web-mobile:latest .
if %errorlevel% neq 0 (
    echo ❌ Error construyendo Docker image
    exit /b 1
)
echo ✅ Imagen Docker construida!
echo 🚀 Ejecutar con: docker run -p 8080:8080 ip-web-mobile:latest
goto end

:local
echo 💻 Ejecutando test local...
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    exit /b 1
)

echo 🧪 Ejecutando tests...
python test_system.py

echo 🚀 Iniciando aplicación local...
echo 📱 Abre http://localhost:8080 en tu navegador
python mobile_web.py
goto end

:end
pause