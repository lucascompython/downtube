#!/usr/bin/env python3

import subprocess
import sys
import argparse


def arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the app")
    parser.add_argument("-r", "--release", action="store_true", help="Build the app in release mode")
    parser.add_argument("-d", "--dev", action="store_true", help="Build the app in development mode")

    return parser.parse_args()

def main(args: argparse.Namespace):
    if args.release and args.dev:
        print("You can't build the app in both release and development mode")
        exit(1)
    
    if not args.release and not args.dev:
        print("You must specify either the release or development mode")
        exit(1)
    
    OS = sys.platform
    match OS:
        case "linux" | "linux2": # admiting that all linux distros come with python3 installed
            import importlib.util

            if importlib.util.find_spec("yt_dlp"):
                print("yt-dlp is already installed")
            else:
                print("Installing yt-dlp")
                subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"])
                print("yt-dlp installed")

        case "win32" | "darwin":
            print(f"{OS} does not come with python3 pre-installed thus embedding yt-dlp in the executable...")
            suffix = ".exe" if OS == "win32" else "_macos"
            print(f"Downloading yt-dlp{suffix}...")

            import json
            import urllib.request
            import os.path

            if not os.path.isfile(f"yt-dlp{suffix}"):
                print(f"yt-dlp{suffix} not found, downloading...")
                with urllib.request.urlopen(f"https://github.com/yt-dlp/yt-dlp/releases/download/2023.02.17/yt-dlp{suffix}") as response:
                    with open(f"yt-dlp{suffix}", "wb") as f:
                        f.write(response.read())

                print(f"yt-dlp{suffix} downloaded!")
            else:
                print(f"yt-dlp{suffix} already exists, skipping download")

            with open("./src-tauri/tauri.conf.json", "r") as f:
                data = json.load(f)
            
            external_bin = data["tauri"]["bundle"]["externalBin"]
            if f"../yt-dlp{suffix}" in external_bin:
                print("yt-dlp is already set to be embedded!")
            else:
                external_bin.append(f"../yt-dlp{suffix}")
                with open("./src-tauri/tauri.conf.json", "w") as f:
                    json.dump(data, f, indent=4)
                print("yt-dlp added to the list of external binaries to be embedded")

        case _:
            print(f"Unsupported OS: {OS}")
            exit(1)

    print("Building the app...")
    if args.release:
        subprocess.run(["pnpm", "tauri", "build"])
    elif args.dev:
        subprocess.run(["pnpm", "tauri", "dev"])
    else:
        print("Something went wrong")
        exit(1)






if __name__ == "__main__":
    try:
        args = arg_parser()
        main(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        exit(0)
else:
    print("This script is not intended to be imported")
    exit(1)

