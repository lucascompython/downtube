import os

import uvicorn
import yt_dlp
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTasks

app = FastAPI()

PORT = 6969
lasts = {}




def _get_info(id: str):
    # only extract info without downloading
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(
            f'https://www.youtube.com/watch?v={id}',
            download=False,
        )
    global lasts
    lasts[id] = info['title']
    return ydl.sanitize_info(info)


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
        ydl.download([f'https://www.youtube.com/watch?v={id}'])



def _cleanup(name: str) -> None:
    os.remove(name)

@app.get("/download")
def download(background_tasks: BackgroundTasks, vid_id: str, audio: bool = False):
    #await run_in_threadpool(_download_video, audio, vid_id)
    _download_video(audio, vid_id)

    ext = '.mp3' if audio else '.mp4'

    name = lasts[vid_id] + ext
    
    background_tasks.add_task(_cleanup, name)
    return FileResponse(name)


@app.get("/info")
def info(vid_id: str):
    info = _get_info(vid_id)
    return JSONResponse(info)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")