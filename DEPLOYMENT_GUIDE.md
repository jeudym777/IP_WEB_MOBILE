# Deploy en Railway.app

## 🚀 Deployment Instructions for Railway

Railway es una plataforma moderna para deployment que detecta automáticamente aplicaciones Python y las despliega.

### 📋 Preparación

1. **Cuenta en Railway**: Regístrate en [railway.app](https://railway.app)
2. **GitHub Connected**: Conecta tu cuenta de GitHub con Railway
3. **Repositorio Público**: Asegúrate de que tu repo esté público

### 🛠️ Configuración Automática

Railway detectará automáticamente:
- ✅ `requirements.txt` - Instalará dependencias Python
- ✅ `Dockerfile` - Usará containerización Docker
- ✅ Puerto 8080 - Para la aplicación web

### 🎯 Deploy Steps

1. **Import Project**:
   - Ve a Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Elige: `jeudym777/IP_WEB_MOBILE`

2. **Environment Variables**:
   ```
   PYTHONPATH=/app
   FLET_WEB_USE_COLOR_EMOJI=true
   PORT=8080
   ```

3. **Custom Start Command**:
   ```bash
   python mobile_web.py
   ```

### 🌐 URLs del Deploy

Después del deploy obtendrás:
- **Web App**: `https://your-app.railway.app`
- **Custom Domain**: Configurable en settings

### 📊 Monitoring

Railway proporciona:
- 📈 **Metrics**: CPU, RAM, Network
- 📝 **Logs**: Logs en tiempo real
- 🔧 **Settings**: Variables de entorno
- 💰 **Usage**: Billing y recursos

---

# Deploy en Render.com

## 🚀 Deployment Instructions for Render

Render es perfecto para aplicaciones Python con deployment automático desde Git.

### 📋 Preparación

1. **Cuenta en Render**: Regístrate en [render.com](https://render.com)
2. **Connect GitHub**: Autoriza acceso a tu repositorio
3. **Free Tier**: Disponible para proyectos pequeños

### 🛠️ Configuración

1. **New Web Service**:
   - Dashboard → "New Web Service"
   - Connect repository: `jeudym777/IP_WEB_MOBILE`
   - Name: `ip-web-mobile`

2. **Build Settings**:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python mobile_web.py`

3. **Environment Variables**:
   ```
   PYTHON_VERSION=3.10.0
   FLET_WEB_USE_COLOR_EMOJI=true
   ```

### 🌍 Features

- **Auto Deploy**: Push to GitHub = Auto deploy
- **Custom Domains**: Tu propio dominio
- **SSL**: HTTPS automático
- **Scaling**: Auto-scaling disponible

---

# Deploy en Vercel

## ⚡ Deployment Instructions for Vercel

Vercel es excelente para aplicaciones frontend, pero requiere configuración especial para Python.

### 📋 Configuración Vercel

Crear `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "mobile_web.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "mobile_web.py"
    }
  ]
}
```

### 🛠️ API Route

Crear `api/index.py`:
```python
from mobile_web import main
import flet as ft

def handler(request, response):
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
```

---

# Deploy en Heroku

## 🏗️ Deployment Instructions for Heroku

Heroku es una plataforma clásica con soporte robusto para Python.

### 📋 Files Needed

1. **Procfile**:
   ```
   web: python mobile_web.py
   worker: python desktop_receiver.py
   ```

2. **runtime.txt**:
   ```
   python-3.10.15
   ```

3. **Aptfile** (para OpenCV):
   ```
   libgl1-mesa-glx
   libglib2.0-0
   ```

### 🚀 Deploy Commands

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create ip-web-mobile

# Set buildpacks
heroku buildpacks:add --index 1 heroku-community/apt
heroku buildpacks:add --index 2 heroku/python

# Deploy
git push heroku master
```

### ⚙️ Configuration

```bash
# Environment variables
heroku config:set FLET_WEB_USE_COLOR_EMOJI=true
heroku config:set PYTHONPATH=/app

# Scale dynos
heroku ps:scale web=1 worker=1
```