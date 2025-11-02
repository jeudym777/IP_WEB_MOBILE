#!/usr/bin/env python3
"""
Build Script para Cloudflare Pages
Genera archivos optimizados para deployment en Cloudflare
"""

import os
import shutil
import json
from pathlib import Path

def create_build_directory():
    """Crea el directorio de build."""
    build_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    return build_dir

def copy_static_files(build_dir):
    """Copia archivos estáticos necesarios."""
    
    # Crear estructura de directorios
    (build_dir / "app").mkdir()
    (build_dir / "assets").mkdir()
    (build_dir / "api").mkdir()
    
    # Copiar archivos de configuración
    files_to_copy = [
        "_redirects",
        "_headers", 
        "wrangler.toml"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy(file, build_dir / file)
    
    # Copiar assets si existen
    if Path("assets").exists():
        shutil.copytree("assets", build_dir / "assets", dirs_exist_ok=True)

def generate_app_html(build_dir):
    """Genera el HTML principal de la aplicación."""
    
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 IP Camera Mobile Web</title>
    <meta name="description" content="Sistema de cámara IP móvil con Cloudflare Edge">
    <meta name="theme-color" content="#667eea">
    
    <!-- PWA Support -->
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/assets/icon-192.png">
    
    <style>
        :root {
            --primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --light: #f8f9fa;
            --dark: #343a40;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 450px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: var(--primary);
            opacity: 0.03;
            animation: rotate 20s linear infinite;
            z-index: -1;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .title {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: var(--primary);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
            font-size: 1.1rem;
        }
        
        .button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0.5rem;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .button:active {
            transform: translateY(-1px);
        }
        
        .button.secondary {
            background: var(--light);
            color: var(--dark);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .status {
            background: var(--light);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            border-left: 4px solid var(--success);
            text-align: left;
        }
        
        .status-title {
            font-weight: 600;
            color: var(--success);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .video-container {
            margin-top: 1.5rem;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            background: var(--dark);
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .video-placeholder {
            color: #666;
            font-size: 3rem;
        }
        
        video {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .controls {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 1.5rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        
        .stat {
            background: white;
            padding: 0.8rem;
            border-radius: 10px;
            border: 2px solid var(--light);
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 1.5rem;
                margin: 0.5rem;
            }
            .title {
                font-size: 2rem;
            }
            .controls {
                flex-direction: column;
            }
            .button {
                width: 100%;
                margin: 0.25rem 0;
            }
        }
        
        .cloudflare-badge {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: #f38020;
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 5px;
            font-size: 0.7rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="cloudflare-badge">⚡ Cloudflare Edge</div>
        
        <div class="title">📱 IP Camera</div>
        <div class="subtitle">
            Sistema de cámara móvil<br>
            <strong>Powered by Cloudflare Workers</strong>
        </div>
        
        <div class="status" id="system-status">
            <div class="status-title">🌐 Sistema Activo</div>
            Edge Network: Global<br>
            Latencia: Ultra-Baja<br>
            SSL: Automático
        </div>

        <div class="controls">
            <button class="button" id="start-camera" onclick="startCamera()">
                📹 Iniciar Cámara
            </button>
            
            <button class="button secondary" onclick="checkStatus()">
                📊 Estado
            </button>
        </div>

        <div class="video-container" id="video-container">
            <div class="video-placeholder">📹</div>
        </div>

        <div class="stats" id="stats" style="display: none;">
            <div class="stat">
                <div class="stat-value" id="frame-count">0</div>
                <div>Frames</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="fps-count">0</div>
                <div>FPS</div>
            </div>
        </div>

        <div id="status-display" style="margin-top: 1rem;"></div>
    </div>

    <script>
        let stream = null;
        let capturing = false;
        let frameCount = 0;
        let lastFrameTime = Date.now();
        let fps = 0;

        // Verificar soporte del navegador
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            document.getElementById('status-display').innerHTML = 
                '<div style="color: red; background: #ffe6e6; padding: 1rem; border-radius: 10px;">' +
                '❌ Tu navegador no soporta acceso a cámara<br>' +
                'Usa Chrome, Firefox o Safari moderno</div>';
        }

        async function startCamera() {
            const button = document.getElementById('start-camera');
            const statusDiv = document.getElementById('status-display');
            const videoContainer = document.getElementById('video-container');
            
            try {
                button.innerHTML = '<div class="loading"></div> Iniciando...';
                button.disabled = true;
                
                statusDiv.innerHTML = '<div style="color: orange; background: #fff3cd; padding: 1rem; border-radius: 10px;">🔄 Solicitando acceso a cámara...</div>';

                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    }
                });

                // Crear y configurar elemento de video
                const video = document.createElement('video');
                video.srcObject = stream;
                video.autoplay = true;
                video.playsinline = true;
                video.muted = true;

                videoContainer.innerHTML = '';
                videoContainer.appendChild(video);

                // Iniciar captura cuando el video esté listo
                video.onloadedmetadata = () => {
                    capturing = true;
                    captureFrames(video);
                    
                    statusDiv.innerHTML = '<div style="color: green; background: #d4edda; padding: 1rem; border-radius: 10px;">✅ Cámara activa - Transmitiendo a Cloudflare Edge</div>';
                    button.innerHTML = '⏹️ Detener';
                    button.onclick = stopCamera;
                    button.disabled = false;
                    
                    document.getElementById('stats').style.display = 'grid';
                };

            } catch (error) {
                console.error('Error accessing camera:', error);
                let errorMessage = 'Error desconocido';
                
                if (error.name === 'NotAllowedError') {
                    errorMessage = 'Acceso denegado - Permite el uso de cámara';
                } else if (error.name === 'NotFoundError') {
                    errorMessage = 'No se encontró cámara disponible';
                } else if (error.name === 'NotSupportedError') {
                    errorMessage = 'Navegador no compatible';
                }
                
                statusDiv.innerHTML = '<div style="color: red; background: #f8d7da; padding: 1rem; border-radius: 10px;">❌ ' + errorMessage + '</div>';
                button.innerHTML = '📹 Iniciar Cámara';
                button.onclick = startCamera;
                button.disabled = false;
            }
        }

        function stopCamera() {
            capturing = false;
            
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }
            
            document.getElementById('video-container').innerHTML = '<div class="video-placeholder">📹</div>';
            document.getElementById('status-display').innerHTML = '<div style="color: orange; background: #fff3cd; padding: 1rem; border-radius: 10px;">⏸️ Cámara detenida</div>';
            document.getElementById('stats').style.display = 'none';
            
            const button = document.getElementById('start-camera');
            button.innerHTML = '📹 Iniciar Cámara';
            button.onclick = startCamera;
            button.disabled = false;
            
            frameCount = 0;
            fps = 0;
        }

        function captureFrames(video) {
            if (!capturing) return;

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;

            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob(async (blob) => {
                if (blob && capturing) {
                    const reader = new FileReader();
                    reader.onload = async () => {
                        await sendFrame(reader.result);
                        updateStats();
                    };
                    reader.readAsDataURL(blob);
                }
            }, 'image/jpeg', 0.8);

            // Siguiente frame en 100ms (10 FPS)
            setTimeout(() => captureFrames(video), 100);
        }

        async function sendFrame(frameData) {
            try {
                const response = await fetch('/api/frame', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        frame: frameData,
                        timestamp: Date.now(),
                        frameNumber: ++frameCount,
                        source: 'cloudflare-pages'
                    })
                });

                if (!response.ok) {
                    console.warn('Frame send failed:', response.status);
                }

            } catch (error) {
                console.error('Error sending frame:', error);
            }
        }

        function updateStats() {
            const now = Date.now();
            const timeDiff = (now - lastFrameTime) / 1000;
            fps = Math.round(1 / timeDiff);
            lastFrameTime = now;
            
            document.getElementById('frame-count').textContent = frameCount;
            document.getElementById('fps-count').textContent = fps;
        }

        async function checkStatus() {
            try {
                const response = await fetch('/api/health');
                const status = await response.json();
                
                document.getElementById('status-display').innerHTML = 
                    '<div style="color: green; background: #d4edda; padding: 1rem; border-radius: 10px;">' +
                    '✅ Sistema: ' + status.status + '<br>' +
                    '📊 Worker: ' + status.worker + '<br>' +
                    '🌍 Edge: Global Network<br>' +
                    '⏰ ' + new Date(status.timestamp).toLocaleString() + '</div>';

            } catch (error) {
                document.getElementById('status-display').innerHTML = 
                    '<div style="color: red; background: #f8d7da; padding: 1rem; border-radius: 10px;">❌ Error verificando estado del sistema</div>';
            }
        }

        // Auto-check status on load
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(checkStatus, 1000);
        });
    </script>
</body>
</html>
    """
    
    with open(build_dir / "app" / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content.strip())

def generate_manifest(build_dir):
    """Genera el manifest para PWA."""
    
    manifest = {
        "name": "IP Camera Mobile Web",
        "short_name": "IP Camera",
        "description": "Sistema de cámara IP móvil con Cloudflare Edge",
        "start_url": "/app/",
        "display": "standalone",
        "theme_color": "#667eea",
        "background_color": "#ffffff",
        "icons": [
            {
                "src": "/assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/assets/icon-512.png", 
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    
    with open(build_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

def generate_index_redirect(build_dir):
    """Genera página de redirección en root."""
    
    redirect_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=/app/">
    <script>window.location.href='/app/';</script>
    <title>Redirecting to IP Camera App...</title>
</head>
<body>
    <p>Redirecting to <a href="/app/">IP Camera App</a>...</p>
</body>
</html>
    """
    
    with open(build_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(redirect_html.strip())

def main():
    """Función principal del build."""
    print("🚀 Building for Cloudflare Pages...")
    
    # Crear directorio de build
    build_dir = create_build_directory()
    print(f"✅ Created build directory: {build_dir}")
    
    # Copiar archivos estáticos
    copy_static_files(build_dir)
    print("✅ Copied static files")
    
    # Generar HTML principal
    generate_app_html(build_dir)
    print("✅ Generated app HTML")
    
    # Generar manifest PWA
    generate_manifest(build_dir)
    print("✅ Generated PWA manifest")
    
    # Generar página de redirección
    generate_index_redirect(build_dir)
    print("✅ Generated index redirect")
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Output directory: {build_dir.resolve()}")
    print("🌐 Ready for Cloudflare Pages deployment")

if __name__ == "__main__":
    main()