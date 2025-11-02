#!/usr/bin/env python3
"""
Test System - Verificador del Sistema de Cámara IP Móvil
Verifica que todos los componentes funcionen correctamente
"""

import subprocess
import sys
import time
import threading
import requests
from pathlib import Path

def print_header():
    """Imprime el header del test."""
    print("=" * 60)
    print("🧪 TEST SYSTEM - VERIFICADOR DE COMPONENTES")
    print("=" * 60)
    print()

def check_dependencies():
    """Verifica las dependencias necesarias."""
    print("📋 Verificando dependencias...")
    
    try:
        import flet
        print(f"✅ Flet: {flet.__version__}")
    except ImportError:
        print("❌ Flet no está instalado")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV no está instalado")
        return False
    
    try:
        import requests
        print(f"✅ Requests disponible")
    except ImportError:
        print("❌ Requests no está instalado")
        return False
    
    print()
    return True

def test_web_server():
    """Prueba el servidor web."""
    print("🌐 Iniciando test del servidor web...")
    
    try:
        # Iniciar el servidor web en un hilo separado
        import mobile_web
        
        def run_web_server():
            import flet as ft
            ft.app(target=mobile_web.main, port=8080, view=None)
        
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        
        # Esperar a que se inicie
        time.sleep(3)
        
        # Probar conectividad
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor web iniciado correctamente en puerto 8080")
            return True
        else:
            print(f"❌ Error en servidor web: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error iniciando servidor web: {e}")
        return False

def test_desktop_receiver():
    """Prueba el receptor de desktop."""
    print("🖥️ Iniciando test del receptor desktop...")
    
    try:
        # Iniciar el receptor en un hilo separado
        import desktop_receiver
        
        def run_desktop_receiver():
            import flet as ft
            ft.app(target=desktop_receiver.main, view=None)
        
        desktop_thread = threading.Thread(target=run_desktop_receiver, daemon=True)
        desktop_thread.start()
        
        # Esperar a que se inicie
        time.sleep(3)
        
        # Probar el endpoint de frames
        test_data = {
            "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "timestamp": int(time.time() * 1000),
            "frameNumber": 1
        }
        
        response = requests.post("http://localhost:8081/frame", 
                               json=test_data, timeout=5)
        
        if response.status_code == 200:
            print("✅ Receptor desktop iniciado correctamente en puerto 8081")
            return True
        else:
            print(f"❌ Error en receptor desktop: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error iniciando receptor desktop: {e}")
        return False

def test_file_structure():
    """Verifica la estructura de archivos."""
    print("📁 Verificando estructura de archivos...")
    
    required_files = [
        "main.py",
        "mobile_web.py", 
        "desktop_receiver.py",
        "start.py",
        "src/ui/main_window.py",
        "src/camera/stream_manager.py",
        "src/network/discovery.py",
        "src/utils/config_manager.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Todos los archivos necesarios están presentes")
        return True

def test_imports():
    """Verifica que todos los módulos se importen correctamente."""
    print("🔍 Verificando imports...")
    
    modules_to_test = [
        "src.ui.main_window",
        "src.camera.stream_manager", 
        "src.network.discovery",
        "src.utils.config_manager",
        "src.utils.logger"
    ]
    
    import_errors = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            import_errors.append(module)
    
    return len(import_errors) == 0

def main():
    """Función principal del test."""
    print_header()
    
    # Lista de tests
    tests = [
        ("Dependencias", check_dependencies),
        ("Estructura de archivos", test_file_structure),
        ("Imports de módulos", test_imports),
        ("Servidor web", test_web_server),
        ("Receptor desktop", test_desktop_receiver)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error en test '{test_name}': {e}")
            results[test_name] = False
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResultado: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡Todos los tests pasaron! El sistema está listo.")
        print("\n📱 Para usar el sistema:")
        print("1. Ejecuta: python start.py")
        print("2. Selecciona '🌐 App Web para Móvil'")
        print("3. Abre la URL en tu móvil")
        print("4. En otra terminal, ejecuta el Desktop Receiver")
    else:
        print("⚠️ Algunos tests fallaron. Revisa los errores arriba.")
    
    print("="*60)

if __name__ == "__main__":
    main()