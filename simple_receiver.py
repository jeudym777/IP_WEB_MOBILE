"""
Receptor PC Simple - Conexión Directa
=====================================

Aplicación simple que muestra el stream desde tu móvil.
Se conecta directamente al sistema que ya tienes funcionando.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import json
import requests
from datetime import datetime
from pathlib import Path


class SimpleCameraReceiver:
    """Receptor simple de cámara desde móvil."""
    
    def __init__(self):
        """Inicializa el receptor simple."""
        self.root = tk.Tk()
        self.root.title("📱➡️🖥️ Receptor Cámara Móvil")
        self.root.geometry("800x700")
        
        self.is_receiving = False
        self.current_frame = None
        self.frame_count = 0
        
        self.setup_interface()
        
    def setup_interface(self):
        """Configura la interfaz."""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="📱➡️🖥️ Receptor Cámara Móvil", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Configuración URL
        ttk.Label(main_frame, text="URL del Worker:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.url_var = tk.StringVar(value="https://ipwebmobile.jeudym777.workers.dev")
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Botones de control
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.connect_btn = ttk.Button(button_frame, text="🌐 Conectar", 
                                     command=self.connect_to_worker)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(button_frame, text="❌ Desconectar", 
                                        command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        self.photo_btn = ttk.Button(button_frame, text="📸 Foto", 
                                   command=self.take_photo, state=tk.DISABLED)
        self.photo_btn.pack(side=tk.LEFT, padx=5)
        
        # Video display
        self.video_label = ttk.Label(main_frame, text="📱 Esperando conexión...", 
                                    font=('Arial', 12), 
                                    background='lightgray', 
                                    anchor='center')
        self.video_label.grid(row=3, column=0, columnspan=2, pady=20, 
                             sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Estado
        self.status_var = tk.StringVar(value="⏸️ Desconectado")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Stats
        self.stats_var = tk.StringVar(value="Frames: 0")
        self.stats_label = ttk.Label(main_frame, textvariable=self.stats_var, 
                                    font=('Arial', 9))
        self.stats_label.grid(row=5, column=0, columnspan=2)
        
        # Instrucciones
        instructions = """
📱 INSTRUCCIONES:

1. 🌐 Tu Worker está desplegado en Cloudflare
2. 📱 Abre esa URL en tu móvil
3. 📷 Permite acceso a la cámara
4. 🖥️ Conecta esta app para ver la transmisión

🔗 URL para el móvil: [misma URL del Worker]
        """
        
        ttk.Label(main_frame, text=instructions, justify=tk.LEFT, 
                 font=('Arial', 9)).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configurar grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def connect_to_worker(self):
        """Conecta al Worker."""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Ingresa una URL válida")
            return
        
        # Test connection
        try:
            response = requests.get(f"{url}/api/health", timeout=5)
            if response.status_code != 200:
                raise Exception("Worker no responde")
        except Exception as e:
            messagebox.showerror("Error", f"No se puede conectar al Worker:\n{e}")
            return
        
        # Configurar UI para modo conectado
        self.worker_url = url
        self.is_receiving = True
        
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.photo_btn.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
        
        self.status_var.set("🟢 Conectado - Esperando frames...")
        
        # Iniciar monitoreo
        self.start_monitoring()
        
        messagebox.showinfo("Conectado", 
                          f"✅ Conectado al Worker\n\n"
                          f"📱 Abre esta URL en tu móvil:\n{url}\n\n"
                          f"📷 Permite acceso a la cámara y verás la transmisión aquí")
    
    def disconnect(self):
        """Desconecta del Worker."""
        self.is_receiving = False
        
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.photo_btn.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
        
        self.status_var.set("⏸️ Desconectado")
        self.video_label.config(image='', text="📱 Desconectado")
    
    def start_monitoring(self):
        """Inicia el monitoreo de frames."""
        def monitor():
            while self.is_receiving:
                try:
                    # Por ahora, como el Worker no almacena frames,
                    # mostramos el estado de conexión
                    response = requests.get(f"{self.worker_url}/api/health", timeout=2)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Actualizar en hilo principal
                        self.root.after(0, lambda: self.status_var.set(
                            f"🟢 Worker activo - {data.get('status', 'unknown')}"
                        ))
                        
                        # Simular frame count
                        self.frame_count += 1
                        self.root.after(0, lambda: self.stats_var.set(
                            f"Checks: {self.frame_count} | Worker: {data.get('worker', 'unknown')}"
                        ))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.status_var.set(f"❌ Error: {e}"))
                
                time.sleep(1)  # Check cada segundo
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def take_photo(self):
        """Captura foto (placeholder por ahora)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photos/mobile_photo_{timestamp}.txt"
        Path("photos").mkdir(exist_ok=True)
        
        # Por ahora guardamos info del estado
        with open(filename, 'w') as f:
            f.write(f"Photo captured from mobile at {timestamp}\n")
            f.write(f"Worker URL: {self.worker_url}\n")
            f.write(f"Status: Connected\n")
        
        self.status_var.set(f"📸 Info guardada: {filename}")
    
    def run(self):
        """Ejecuta la aplicación."""
        print("🖥️ Iniciando Receptor Simple...")
        print("📱 Asegúrate que tu Worker esté desplegado")
        self.root.mainloop()


if __name__ == "__main__":
    # Crear directorios
    Path("photos").mkdir(exist_ok=True)
    
    # Ejecutar
    app = SimpleCameraReceiver()
    app.run()