@echo off
echo =====================================================
echo 📱 SISTEMA DE CAMARA IP MOVIL 📱
echo =====================================================
echo.
echo Este sistema permite usar tu celular como camara IP
echo y ver la transmision en tu PC desktop.
echo.
echo PASOS:
echo 1. Tu celular y PC deben estar en la MISMA RED WIFI
echo 2. Primero ejecuta el RECEPTOR en tu PC
echo 3. Luego abre la APP WEB en tu celular
echo.
echo =====================================================
echo.

:menu
echo Selecciona una opcion:
echo.
echo [1] Iniciar RECEPTOR Desktop (ejecutar primero en PC)
echo [2] Iniciar APP WEB para celular
echo [3] Ver IP de esta PC
echo [4] Salir
echo.
set /p choice="Ingresa tu opcion (1-4): "

if "%choice%"=="1" goto desktop
if "%choice%"=="2" goto mobile
if "%choice%"=="3" goto showip
if "%choice%"=="4" goto exit

echo Opcion invalida, intenta de nuevo.
goto menu

:desktop
echo.
echo 🖥️ Iniciando RECEPTOR Desktop...
echo ===============================
echo.
echo La aplicacion se abrira en una ventana.
echo Deja esta ventana abierta para recibir el video del celular.
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.
python desktop_receiver.py
pause
goto menu

:mobile
echo.
echo 📱 Iniciando APP WEB para celular...
echo ===================================
echo.
echo La aplicacion web se iniciara en tu navegador.
echo.
echo Para usar desde tu CELULAR:
echo 1. Averigua la IP de esta PC (opcion 3)
echo 2. En tu celular, abre el navegador
echo 3. Ve a: http://[IP_DE_ESTA_PC]:8080
echo.
echo Ejemplo: http://192.168.1.100:8080
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.
python mobile_web.py
pause
goto menu

:showip
echo.
echo 🌐 IP de esta PC:
echo ===============
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo %%b
    )
)
echo.
echo Usa esta IP para conectar desde tu celular.
echo Ejemplo: http://[IP_MOSTRADA_ARRIBA]:8080
echo.
pause
goto menu

:exit
echo.
echo 👋 Gracias por usar el Sistema de Camara IP Movil!
echo.
pause
exit