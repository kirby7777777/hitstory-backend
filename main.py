from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import yt_dlp

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
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                return RedirectResponse(url=video['url'])
            elif 'url' in info:
                return RedirectResponse(url=info['url'])
            else:
                raise HTTPException(status_code=404, detail="Audio no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))