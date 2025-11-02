/**
 * Cloudflare Worker para IP Camera Mobile Web System
 * Maneja requests y sirve la aplicación Python Flet
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Headers CORS para cámaras móviles
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    };

    // Manejar preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: corsHeaders
      });
    }

    try {
      // API Routes para frames de cámara
      if (path.startsWith('/api/')) {
        return handleAPI(request, env, corsHeaders);
      }

      // Servir aplicación Flet
      if (path === '/' || path.startsWith('/app/')) {
        return serveApp(request, env, corsHeaders);
      }

      // Assets estáticos
      if (path.startsWith('/assets/')) {
        return serveAssets(request, env, corsHeaders);
      }

      // Fallback a aplicación principal
      return serveApp(request, env, corsHeaders);

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({
        error: 'Internal Server Error',
        message: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  }
};

/**
 * Maneja las API calls para frames de cámara
 */
async function handleAPI(request, env, corsHeaders) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Endpoint para recibir frames de cámara móvil
  if (path === '/api/frame' && request.method === 'POST') {
    try {
      const frameData = await request.json();
      
      // Validar datos del frame
      if (!frameData.frame || !frameData.timestamp) {
        return new Response(JSON.stringify({
          error: 'Invalid frame data',
          required: ['frame', 'timestamp']
        }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }

      // Almacenar frame temporalmente en memoria (para el último frame)
      // Esto permite que el PC pueda obtener el frame más reciente
      global.latestFrame = {
        frame: frameData.frame,
        timestamp: frameData.timestamp,
        frameNumber: frameData.frameNumber || 0,
        receivedAt: Date.now()
      };
      
      // Mantener solo el último frame para streaming en tiempo real
      global.frameHistory = global.frameHistory || [];
      global.frameHistory.push(global.latestFrame);
      
      // Mantener solo los últimos 10 frames
      if (global.frameHistory.length > 10) {
        global.frameHistory = global.frameHistory.slice(-10);
      }

      // Log para debugging
      console.log(`Frame received: ${frameData.frameNumber || 'unknown'} at ${new Date(frameData.timestamp).toISOString()}`);

      return new Response(JSON.stringify({
        status: 'success',
        message: 'Frame received',
        timestamp: Date.now()
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });

    } catch (error) {
      console.error('Frame processing error:', error);
      return new Response(JSON.stringify({
        error: 'Frame processing failed',
        message: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  }

  // Endpoint para obtener frames recientes
  if (path === '/api/frames' && request.method === 'GET') {
    try {
      // Obtener frames desde memoria temporal
      const frames = global.frameHistory || [];
      const latestFrame = global.latestFrame || null;
      
      // Respuesta con frames disponibles
      return new Response(JSON.stringify({
        frames: frames,
        latestFrame: latestFrame,
        count: frames.length,
        timestamp: Date.now(),
        message: frames.length > 0 ? 'Frames available from mobile device' : 'No frames received yet'
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });

    } catch (error) {
      console.error('Frames retrieval error:', error);
      return new Response(JSON.stringify({
        error: 'Failed to retrieve frames',
        message: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  }

  // Endpoint para obtener solo el último frame (más eficiente)
  if (path === '/api/latest-frame' && request.method === 'GET') {
    try {
      const latestFrame = global.latestFrame || null;
      
      if (latestFrame) {
        return new Response(JSON.stringify({
          success: true,
          frame: latestFrame,
          timestamp: Date.now()
        }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      } else {
        return new Response(JSON.stringify({
          success: false,
          message: 'No frame available yet',
          timestamp: Date.now()
        }), {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }
    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to get latest frame',
        message: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  }

  // Endpoint para health check
  if (path === '/api/health' && request.method === 'GET') {
    const framesCount = global.frameHistory ? global.frameHistory.length : 0;
    const hasLatestFrame = !!global.latestFrame;
    
    return new Response(JSON.stringify({
      status: 'healthy',
      timestamp: Date.now(),
      worker: 'ip-camera-mobile-web',
      version: '2.1.0',
      framesReceived: framesCount,
      latestFrameAvailable: hasLatestFrame,
      lastFrameTime: global.latestFrame ? global.latestFrame.receivedAt : null
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }

  // API endpoint no encontrado
  return new Response(JSON.stringify({
    error: 'API endpoint not found',
    path: path,
    method: request.method
  }), {
    status: 404,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders
    }
  });
}

/**
 * Sirve la aplicación Flet principal
 */
async function serveApp(request, env, corsHeaders) {
  // HTML básico que carga la aplicación Flet
  const html = `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 IP Camera Mobile Web</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        .title {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #333;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.5;
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 0.5rem;
            text-decoration: none;
            display: inline-block;
        }
        .button:hover {
            transform: translateY(-2px);
        }
        .status {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #28a745;
        }
        @media (max-width: 480px) {
            .container {
                padding: 1.5rem;
                margin: 1rem;
            }
            .title {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">📱 IP Camera Mobile</div>
        <div class="subtitle">
            Sistema de cámara móvil powered by Cloudflare Workers
        </div>
        
        <div class="status">
            <strong>🌐 Sistema Activo</strong><br>
            Cloudflare Edge Network<br>
            Latencia Ultra-Baja
        </div>

        <button class="button" onclick="startCamera()">
            📹 Iniciar Cámara
        </button>
        
        <button class="button" onclick="checkStatus()">
            📊 Estado del Sistema
        </button>

        <div id="status-display" style="margin-top: 1rem;"></div>
        <div id="camera-preview" style="margin-top: 1rem;"></div>
    </div>

    <script>
        let stream = null;
        let capturing = false;
        let frameCount = 0;

        async function startCamera() {
            try {
                const statusDiv = document.getElementById('status-display');
                statusDiv.innerHTML = '<div style="color: orange;">🔄 Iniciando cámara...</div>';

                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    }
                });

                // Crear elemento de video
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                video.style.width = '100%';
                video.style.borderRadius = '10px';
                video.style.marginTop = '1rem';

                const preview = document.getElementById('camera-preview');
                preview.innerHTML = '';
                preview.appendChild(video);

                // Iniciar captura de frames
                capturing = true;
                captureFrames(video);

                statusDiv.innerHTML = '<div style="color: green;">✅ Cámara activa - Transmitiendo</div>';

            } catch (error) {
                console.error('Error accessing camera:', error);
                document.getElementById('status-display').innerHTML = 
                    '<div style="color: red;">❌ Error: ' + error.message + '</div>';
            }
        }

        function captureFrames(video) {
            if (!capturing) return;

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;

            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob(async (blob) => {
                if (blob) {
                    const reader = new FileReader();
                    reader.onload = async () => {
                        await sendFrame(reader.result);
                    };
                    reader.readAsDataURL(blob);
                }
            }, 'image/jpeg', 0.8);

            // Capturar siguiente frame en 100ms (10 FPS)
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
                        frameNumber: ++frameCount
                    })
                });

                if (!response.ok) {
                    console.warn('Frame send failed:', response.status);
                }

            } catch (error) {
                console.error('Error sending frame:', error);
            }
        }

        async function checkStatus() {
            try {
                const response = await fetch('/api/health');
                const status = await response.json();
                
                document.getElementById('status-display').innerHTML = 
                    '<div style="color: green;">✅ Sistema: ' + status.status + 
                    '<br>📊 Worker: ' + status.worker + 
                    '<br>⏰ ' + new Date(status.timestamp).toLocaleString() + '</div>';

            } catch (error) {
                document.getElementById('status-display').innerHTML = 
                    '<div style="color: red;">❌ Error checking status</div>';
            }
        }
    </script>
</body>
</html>`;

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html',
      ...corsHeaders
    }
  });
}

/**
 * Sirve assets estáticos
 */
async function serveAssets(request, env, corsHeaders) {
  // Por ahora retorna 404, pero se puede expandir para servir CSS/JS/images
  return new Response('Asset not found', {
    status: 404,
    headers: corsHeaders
  });
}