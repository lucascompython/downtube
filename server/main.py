import asyncio

import aiofiles.os
import uvicorn
import yt_dlp
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

CACHE_SIZE = 200 # max number of video information to cache
PORT = 6969
last_name = ""


def _get_info(id: str):
    # only extract info without downloading
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(
            f'https://www.youtube.com/watch?v={id}',
            download=False,
        )
    global last_name
    last_name = info['title']
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
        #info = ydl.extract_info(
            #f'https://www.youtube.com/watch?v={id}',
            #download=True,
        #)
        ydl.download([f'https://www.youtube.com/watch?v={id}'])

    #if id not in video_info_cache:
        #video_info_cache[id] = ydl.sanitize_info(info)


async def _cleanup():
    dir = await aiofiles.os.listdir()
    for file in dir:
        if file.endswith(".mp3") or file.endswith(".mp4"):
            await aiofiles.os.remove(file)

@app.get("/download")
async def download(vid_id: str, audio: bool = False):
    loop = asyncio.get_event_loop()
    func = loop.run_in_executor(None, _download_video, audio, vid_id)
    await asyncio.gather(func, _cleanup())

    ext = '.mp3' if audio else '.mp4'
    return FileResponse(last_name + ext)


@app.get("/info")
async def info(vid_id: str):
    info = _get_info(vid_id)
    return JSONResponse(info)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")