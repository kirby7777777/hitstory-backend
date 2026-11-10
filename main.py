from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "HITSTORY Backend Activo"}

@app.get("/stream")
def get_stream(q: str):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parámetro 'q' vacío")

    # Intento 1: Extracción vía yt-dlp usando cliente iOS / Android VR (libres de bot check)
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android_vr'],
                'skip': ['webpage']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{q} audio", download=False)
            if info:
                entry = info['entries'][0] if 'entries' in info and len(info['entries']) > 0 else info
                url = entry.get('url')
                if not url and 'formats' in entry:
                    audio_formats = [f for f in entry['formats'] if f.get('acodec') != 'none' and f.get('url')]
                    if audio_formats:
                        url = audio_formats[-1]['url']
                
                if url:
                    return JSONResponse(content={"url": url})
    except Exception as e:
        print(f"yt-dlp falló, probando API Fallback: {e}")

    # Intento 2: Fallback vía API Piped (Respaldo 100% anti-bot para servidores cloud)
    try:
        search_res = requests.get(
            f"https://pipedapi.kavin.rocks/search?q={requests.utils.quote(q)}&filter=music_songs",
            timeout=8
        ).json()
        
        items = search_res.get('items', [])
        if items:
            video_id = items[0]['url'].split('v=')[-1]
            streams_res = requests.get(f"https://pipedapi.kavin.rocks/streams/{video_id}", timeout=8).json()
            audio_streams = streams_res.get('audioStreams', [])
            if audio_streams:
                return JSONResponse(content={"url": audio_streams[0]['url']})
    except Exception as e:
        print(f"Fallback Piped falló: {e}")

    raise HTTPException(status_code=500, detail="No se pudo resolver la URL del audio tras múltiples intentos")