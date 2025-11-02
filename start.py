#!/usr/bin/env python3
"""
🚀 INICIADOR DEL SISTEMA DE CÁMARA IP MÓVIL
==========================================

Script principal para iniciar fácilmente el sistema.
"""

import subprocess
import sys
import socket
import webbrowser
import time
import os
from pathlib import Path


def get_local_ip():
    """Obtiene la IP local de la PC."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def check_python():
    """Verifica que Python esté instalado."""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python encontrado: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python no encontrado")
        return False


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    deps = ["flet", "opencv-python", "numpy"]
    missing = []
    
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep} instalado")
        except ImportError:
            print(f"❌ {dep} faltante")
            missing.append(dep)
    
    return len(missing) == 0, missing


def install_dependencies(missing_deps):
    """Instala dependencias faltantes."""
    print("\n🔧 Instalando dependencias faltantes...")
    for dep in missing_deps:
        print(f"Instalando {dep}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", dep
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {dep} instalado correctamente")
        else:
            print(f"❌ Error instalando {dep}: {result.stderr}")
            return False
    return True


def show_menu():
    """Muestra el menú principal."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 60)
    print("📱 SISTEMA DE CÁMARA IP MÓVIL 📱")
    print("=" * 60)
    print()
    print("Convierte tu celular en una cámara IP profesional")
    print("y ve la transmisión en tiempo real en tu PC.")
    print()
    print("REQUISITOS:")
    print("✅ PC y celular en la MISMA red WiFi")
    print("✅ Navegador web en el celular")
    print("✅ Permisos de cámara en el navegador")
    print()
    print("=" * 60)
    print()
    
    local_ip = get_local_ip()
    print(f"🌐 IP de esta PC: {local_ip}")
    print(f"📱 URL para celular: http://{local_ip}:8080")
    print()
    print("OPCIONES:")
    print("1. 🖥️  Iniciar RECEPTOR Desktop (ejecutar primero)")
    print("2. 📱 Iniciar SERVIDOR Web para celular")
    print("3. 🚀 Iniciar TODO (receptor + servidor)")
    print("4. 🔧 Verificar sistema")
    print("5. 📋 Ver instrucciones detalladas") 
    print("6. 🚪 Salir")
    print()


def start_desktop():
    """Inicia la aplicación desktop."""
    print("🖥️ Iniciando aplicación desktop...")
    print("La ventana del receptor se abrirá automáticamente.")
    print("¡Mantén esta ventana abierta para recibir video del celular!")
    print()
    print("Presiona Ctrl+C para detener.")
    print()
    
    try:
        subprocess.run([sys.executable, "desktop_receiver.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Receptor detenido.")
    except Exception as e:
        print(f"❌ Error: {e}")


def start_web():
    """Inicia el servidor web."""
    local_ip = get_local_ip()
    
    print("📱 Iniciando servidor web...")
    print()
    print("🌐 Servidor disponible en:")
    print(f"   • Desde esta PC: http://localhost:8080")
    print(f"   • Desde tu celular: http://{local_ip}:8080")
    print()
    print("📋 PASOS PARA USAR DESDE EL CELULAR:")
    print("1. Abre el navegador en tu celular")
    print(f"2. Ve a: http://{local_ip}:8080")
    print("3. Permite acceso a la cámara")
    print("4. ¡Configura la IP y transmite!")
    print()
    print("Presiona Ctrl+C para detener.")
    print()
    
    try:
        # Abrir navegador automáticamente
        time.sleep(2)
        webbrowser.open(f"http://localhost:8080")
        
        subprocess.run([sys.executable, "mobile_web.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Servidor web detenido.")
    except Exception as e:
        print(f"❌ Error: {e}")


def start_all():
    """Inicia ambos servicios."""
    print("🚀 Iniciando sistema completo...")
    print()
    
    local_ip = get_local_ip()
    
    try:
        # Iniciar receptor en background
        print("🖥️ Iniciando receptor desktop...")
        desktop_process = subprocess.Popen([sys.executable, "desktop_receiver.py"])
        
        time.sleep(3)  # Esperar a que inicie
        
        # Iniciar servidor web
        print("📱 Iniciando servidor web...")
        print()
        print("🌐 URLs disponibles:")
        print(f"   • PC: http://localhost:8080")
        print(f"   • Celular: http://{local_ip}:8080")
        print()
        print("✅ ¡Sistema listo!")
        print("📱 Abre la URL del celular en tu móvil para comenzar.")
        print()
        print("Presiona Ctrl+C para detener todo.")
        print()
        
        # Abrir navegador
        time.sleep(2)
        webbrowser.open(f"http://localhost:8080")
        
        # Iniciar servidor web (blocking)
        subprocess.run([sys.executable, "mobile_web.py"])
        
    except KeyboardInterrupt:
        print("\n⏹️ Deteniendo sistema...")
        if 'desktop_process' in locals():
            desktop_process.terminate()
        print("✅ Sistema detenido.")
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'desktop_process' in locals():
            desktop_process.terminate()


def verify_system():
    """Verifica el sistema completo."""
    print("🔧 VERIFICACIÓN DEL SISTEMA")
    print("=" * 40)
    print()
    
    # Verificar Python
    if not check_python():
        return False
    
    # Verificar dependencias
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print(f"\n❌ Faltan dependencias: {missing}")
        install = input("\n¿Instalar dependencias faltantes? (s/n): ")
        if install.lower() == 's':
            if install_dependencies(missing):
                print("\n✅ Todas las dependencias instaladas.")
            else:
                print("\n❌ Error instalando dependencias.")
                return False
        else:
            return False
    
    # Verificar archivos
    required_files = ["desktop_receiver.py", "mobile_web.py"]
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} faltante")
            return False
    
    # Verificar red
    local_ip = get_local_ip()
    print(f"✅ IP local: {local_ip}")
    
    # Verificar puertos
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Puerto libre si no se puede conectar
    
    if check_port(8080):
        print("✅ Puerto 8080 libre")
    else:
        print("⚠️ Puerto 8080 ocupado")
    
    if check_port(8081):
        print("✅ Puerto 8081 libre")
    else:
        print("⚠️ Puerto 8081 ocupado")
    
    print("\n✅ Sistema verificado correctamente.")
    return True


def show_instructions():
    """Muestra instrucciones detalladas."""
    print("📋 INSTRUCCIONES DETALLADAS")
    print("=" * 50)
    print()
    print("🎯 OBJETIVO:")
    print("Usar tu celular como cámara IP y ver el video en tu PC.")
    print()
    print("📋 PASOS DETALLADOS:")
    print()
    print("1. 🔧 PREPARACIÓN:")
    print("   • Conecta PC y celular a la MISMA red WiFi")
    print("   • Verifica que ambos dispositivos se vean en la red")
    print()
    print("2. 🖥️ EN LA PC:")
    print("   • Ejecuta opción 1: 'Iniciar RECEPTOR Desktop'")
    print("   • Se abrirá una ventana mostrando tu IP")
    print("   • Anota esa IP (ejemplo: 192.168.1.100)")
    print("   • Deja esta ventana abierta")
    print()
    print("3. 📱 EN EL CELULAR:")
    print("   • Ejecuta opción 2: 'Iniciar SERVIDOR Web'")
    print("   • Se abrirá tu navegador automáticamente")
    print("   • En el celular, ve a: http://[IP_DE_TU_PC]:8080")
    print("   • Ejemplo: http://192.168.1.100:8080")
    print()
    print("4. 🎥 TRANSMITIR:")
    print("   • En la web del celular, ingresa la IP de tu PC")
    print("   • Presiona 'Iniciar Cámara'")
    print("   • Permite acceso a la cámara")
    print("   • ¡El video aparecerá en tu PC!")
    print()
    print("5. 🎬 CONTROLES:")
    print("   • PC: Grabar video, capturar fotos")
    print("   • Celular: Iniciar/detener transmisión")
    print()
    print("⚠️ PROBLEMAS COMUNES:")
    print("• No aparece video: Verifica la IP y la red")
    print("• No accede a cámara: Permite permisos en navegador")
    print("• Conexión lenta: Acércate al router WiFi")
    print()
    print("🎉 ¡DISFRUTA TU NUEVA CÁMARA IP!")


def main():
    """Función principal."""
    while True:
        show_menu()
        
        try:
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                start_desktop()
            elif choice == "2":
                start_web()
            elif choice == "3":
                start_all()
            elif choice == "4":
                verify_system()
            elif choice == "5":
                show_instructions()
            elif choice == "6":
                print("\n👋 ¡Gracias por usar el Sistema de Cámara IP Móvil!")
                break
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.")
            
            if choice in ["1", "2", "3", "4", "5"]:
                input("\nPresiona Enter para volver al menú...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    main()