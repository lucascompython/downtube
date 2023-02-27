# This is Tauri App with NextJs that downloads (and or convert) Youtube videos

## Description

This is a Tauri App with NextJs that downloads and can convert Youtube videos. For that it uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [youtube-dl-rs](https://github.com/GyrosOfWar/youtube-dl-rs)

## Preview

![Preview](https://cdn.discordapp.com/attachments/626449728988774401/1077232713532186725/image.png)

## Build It

```bash
git clone https://github.com/lucascompython/downtube.git
cd downtube
./build.py -h
```

## TODO

- [ ] Add playlist support
- [ ] Update the UI with some more information about the video
- [ ] Remove build.py and use build.rs (didn't know about it)
- [ ] Maybe add mobile support with Tauri 2.0
- [ ] Replace yt-dlp and ffmpeg
