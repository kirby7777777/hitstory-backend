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
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'tv_embedded', 'android']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{q} audio", download=False)
            
            if not info:
                raise HTTPException(status_code=404, detail="No se obtuvo información de la búsqueda")

            # Si devuelve lista de resultados (ytsearch1)
            entry = info['entries'][0] if 'entries' in info and len(info['entries']) > 0 else info

            # Intentar obtener la URL directa
            url = entry.get('url')

            # Si no está en la raíz, buscar dentro de la lista de formatos disponibles
            if not url and 'formats' in entry:
                # Filtrar formatos que sean solo de audio o los de mejor calidad
                audio_formats = [
                    f for f in entry['formats'] 
                    if f.get('acodec') != 'none' and f.get('url')
                ]
                if audio_formats:
                    # Seleccionar el último formato (generalmente la mejor calidad de audio)
                    url = audio_formats[-1]['url']

            if not url:
                raise HTTPException(status_code=404, detail="Audio no encontrado en los formatos disponibles")

            return JSONResponse(content={"url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))