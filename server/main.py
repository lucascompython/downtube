import aiofiles.os
import uvicorn
import yt_dlp
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

CACHE_SIZE = 200 # max number of video information to cache
PORT = 6969
video_info_cache: dict[str, dict] = {}

def _download_video(audio: bool, id: str):
    yt_opts = {
        'format': 'bestaudio/best' if audio else 'bestvideo+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        "external_downloader": "aria2c", # assuming aria2c is installed on every linux system
    }

    if audio:
        yt_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': 'best',
        }]
    else:
        yt_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]

    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        info = ydl.extract_info(
            f'https://www.youtube.com/watch?v={id}',
            download=True,
        )

    if id not in video_info_cache:
        video_info_cache[id] = ydl.sanitize_info(info)


async def _cleanup(id: str, audio: bool):
    name = video_info_cache[id]['title']
    ext = 'mp3' if audio else 'mp4'
    await aiofiles.os.remove(f'{name}.{ext}')

    if len(video_info_cache) > CACHE_SIZE:
        video_info_cache.popitem()


@app.get("/download")
async def download(vid_id: str, audio: bool = False):
    _download_video(audio, vid_id)
    ext = 'mp3' if audio else 'mp4'
    return FileResponse(f'{video_info_cache[vid_id]["title"]}.{ext}')


@app.get("/info")
async def info(vid_id: str, audio: bool = False):
    await _cleanup(vid_id, audio)
    return JSONResponse(video_info_cache[vid_id])


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")