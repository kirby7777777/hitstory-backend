from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yt_dlp
import requests

app = FastAPI()

# Lista de instancias Piped/Invidious redundantes para fallbacks en servidores cloud
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacydev.net",
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.moomoo.me"
]

@app.get("/")
def home():
    return {"status": "HITSTORY Backend Activo"}

@app.get("/stream")
def get_stream(q: str):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parámetro 'q' vacío")

    # Intentar primero con la API de Piped (Respuesta ultra rápida y sin bloqueos de IP)
    for instance in PIPED_INSTANCES:
        try:
            search_req = requests.get(
                f"{instance}/search?q={requests.utils.quote(q)}&filter=music_songs",
                timeout=4
            )
            if search_req.status_code == 200:
                items = search_req.json().get('items', [])
                if items:
                    video_id = items[0]['url'].split('v=')[-1]
                    stream_req = requests.get(f"{instance}/streams/{video_id}", timeout=4)
                    if stream_req.status_code == 200:
                        audio_streams = stream_req.json().get('audioStreams', [])
                        if audio_streams:
                            # Retorna el primer stream de audio directo (generalmente Opus / AAC)
                            return JSONResponse(content={"url": audio_streams[0]['url']})
        except Exception as e:
            print(f"Instancia {instance} falló: {e}")
            continue

    # Fallback con yt-dlp usando cliente mweb/web_embedded si las APIs fallan
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'web_embedded']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{q} audio", download=False)
            if info:
                entry = info['entries'][0] if 'entries' in info and len(info['entries']) > 0 else info
                
                # Buscar URL directa
                url = entry.get('url')
                if not url and 'formats' in entry:
                    for fmt in reversed(entry['formats']):
                        if fmt.get('url') and fmt.get('acodec') != 'none':
                            url = fmt['url']
                            break

                if url:
                    return JSONResponse(content={"url": url})
    except Exception as e:
        print(f"yt-dlp falló: {e}")

    raise HTTPException(status_code=500, detail="No se pudo resolver el flujo de audio")