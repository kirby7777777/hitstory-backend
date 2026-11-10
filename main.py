from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"status": "HITSTORY Backend Activo"}

@app.get("/stream")
def get_stream(q: str):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parámetro 'q' vacío")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        # Configuración para saltarse el bot check en servidores cloud (Render)
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_embedded', 'mweb', 'web_embedded'],
                'skip': ['webpage', 'configs']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (SmartTV; SmartTV; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) InternetClient/2.0.0 Chrome/115.0.0.0 Safari/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{q} audio", download=False)
            url = None
            
            if info:
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    url = entry.get('url')
                elif 'url' in info:
                    url = info.get('url')
            
            if not url:
                raise HTTPException(status_code=404, detail="Audio no encontrado")

            return JSONResponse(content={"url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))