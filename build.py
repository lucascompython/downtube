
import argparse
import asyncio
import json
import os
import subprocess
import sys
from enum import Enum

import aiohttp
from aiofiles import open as aopen

OS = sys.platform

class FFTypes(Enum):
    ffmpeg = 0
    ffprobe = 1


async def _download_yt_dlp(session: aiohttp.ClientSession, suffix: str, ext: str):
    async with session.get(f"https://github.com/yt-dlp/yt-dlp/releases/download/2023.02.17/yt-dlp{ext}") as resp:
        async with aopen(f"yt-dlp{suffix}", "wb") as f:
            await f.write(await resp.read())


async def _download_ffmpeg(session: aiohttp.ClientSession, ff_type: FFTypes, suffix: str):
    ext = ".exe" if OS == "win32" else ""
    async with session.get(f"https://github.com/lucascompython/ffmpeg/releases/download/Binaries/{ff_type.name}{ext}") as resp:
        os.makedirs("ffmpeg", exist_ok=True)
        async with aopen(f"ffmpeg/{ff_type.name}{suffix}", "wb") as f:
            await f.write(await resp.read())

async def download_dependencies(session: aiohttp.ClientSession, suffix: str, ext: str):
    """Downloads yt-dlp and ffmpeg/ffprobe/ffplay if needed

    Args:
        session (aiohttp.ClientSession): The aiohttp session
        suffix (str): The rust target suffix
        ext (str): The extension of the yt-dlp executable
        ff_type (FFTypes): The ffmpeg type to download
        repo (str): The repo to download from
    """
    to_download = []
    if not os.path.isfile(f"yt-dlp{suffix}"):
        print("yt-dlp not found, downloading...")
        to_download.append(_download_yt_dlp(session, suffix, ext))
    else:
        print("yt-dlp found, skipping download")
    
    if not os.path.isdir("ffmpeg"):
        print("ffmpeg not found, downloading...")
        for ff_type in FFTypes:
            to_download.append(_download_ffmpeg(session, ff_type, suffix))
    else:
        print("ffmpeg found, skipping download")
    
    if to_download:
        await asyncio.gather(*to_download)
        print("Dependencies downloaded!")
    

    


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the app")
    parser.add_argument("-r", "--release", action="store_true", help="Build the app in release mode")
    parser.add_argument("-d", "--dev", action="store_true", help="Build the app in development mode")
    parser.add_argument("-s", "--server", action="store_true", help="Build the app with the data fetching from the server so with no dependencies")
    parser.add_argument("-l", "--local", action="store_true", help="Build the app with the data fetching from the local dependencies (yt-dlp and ffmpeg/ffprobe/ffplay ~150mb)")
    parser.add_argument("-v", "--version", action="version", version="downtube v0.1.0")
    

    return parser.parse_args()


def check_node_modules():
    if not os.path.isdir("./client/src-frontend/node_modules"):
        print("node_modules not found, installing...")
        subprocess.run(["pnpm", "i"], cwd="./client/src-frontend", shell=True if OS == "win32" else False)
        print("node_modules installed!")
    else:
        print("node_modules found, skipping install")

def check_dist():
    if not os.path.isdir("./client/dist"):
        print("dist not found, building...")
        os.mkdir("./client/dist")
        print("dist built!")
    else:
        print("dist found, skipping build")

async def main(args: argparse.Namespace):
    if args.release and args.dev:
        print("You can't build the app in both release and development mode")
        exit(1)
    
    if not args.release and not args.dev:
        print("You must specify either the release or development mode")
        exit(1)
    
    if args.server and args.local:
        print("You can't build the app with both the server and local dependencies")
        exit(1)
    
    if not args.server and not args.local:
        print("You must specify either the server or local dependencies")
        exit(1)
    
    check_node_modules()
    check_dist()
    

    tauri_path = "./client/src-tauri-local" if args.local else "./client/src-tauri-server"

    
    with open(f"{tauri_path}/tauri.conf.json", "r") as f:
        tauri_config = json.load(f)
    if args.local:

        external_bin = tauri_config["tauri"]["bundle"]["externalBin"]

        match OS:
            case "linux" | "linux2": # admiting that all linux distros come with python3 and ffmpeg installed 
                import importlib.util

                if importlib.util.find_spec("yt_dlp"):
                    print("yt-dlp is already installed")
                else:
                    print("Installing yt-dlp")
                    subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"])
                    print("yt-dlp installed")
                
                # if any files are embedded, remove them
                if external_bin:
                    print("Removing embedded files...")
                    external_bin.clear()
                    with open("./src-tauri/tauri.conf.json", "w") as f:
                        json.dump(tauri_config, f, indent=4)
                
                    

            case "win32" | "darwin":
                print(f"{OS} does not come with python3 pre-installed thus embedding yt-dlp in the executable...")
                suffix = "-x86_64-pc-windows-msvc.exe" if OS == "win32" else "-x86_64-apple-darwin"
                ext = ".exe" if OS == "win32" else "_macos"

                async with aiohttp.ClientSession() as session:

                    await download_dependencies(session, suffix, ext)


                    
                    if "../../yt-dlp" in external_bin:
                        print("yt-dlp is already set to be embedded!")
                    else:
                        external_bin.append(f"../../yt-dlp")
                    if "../../ffmpeg/*" in external_bin:
                        print("ffmpeg is already set to be embedded!")
                    else:
                        external_bin.append("../../ffmpeg/*")


                    with open(f"{tauri_path}/tauri.conf.json", "w") as f:
                        json.dump(tauri_config, f, indent=4)
            case _:
                print(f"Unsupported OS: {OS}")
                exit(1)
    elif args.server:
        ip = input("Enter the ip and port of the server (e.g. 0.0.0.0:6969) ")
        if not ip:
            print("Defaulting to 0.0.0.0:6969")
            ip = "0.0.0.0:6969"
        ip = "http://" + ip
        with open(f"{tauri_path}/appsettings.json", "w") as f:
            json.dump({"ip": ip}, f, indent=4)
        


    print("Building the app...")
    if args.release:
        subprocess.run(["cargo", "tauri", "build"], cwd=tauri_path, shell=True if OS == "win32" else False)
    elif args.dev:
        subprocess.run(["cargo", "tauri", "dev"], cwd=tauri_path, shell=True if OS == "win32" else False) 

    else:
        print("Something went wrong")
        exit(1)






if __name__ == "__main__":
    try:
        args = arg_parser()
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        exit(0)
else:
    print("This script is not intended to be imported")
    exit(1)

