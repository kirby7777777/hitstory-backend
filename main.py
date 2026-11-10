from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "HITSTORY Backend Activo"}

@app.get("/stream")
def get_stream(q: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{q} audio", download=False)
            url = None
            if 'entries' in info and len(info['entries']) > 0:
                url = info['entries'][0]['url']
            elif 'url' in info:
                url = info['url']
            
            if not url:
                raise HTTPException(status_code=404, detail="Audio no encontrado")

            # Hacemos proxy del flujo de datos con cabeceras de navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            }
            req = requests.get(url, headers=headers, stream=True)
            
            return StreamingResponse(
                req.iter_content(chunk_size=1024 * 64),
                media_type="audio/mpeg"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))