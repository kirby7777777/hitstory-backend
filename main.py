from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"status": "HITSTORY Backend Activo"}

@app.get("/stream")
def get_stream(q: str):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
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

            return JSONResponse(content={"url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))