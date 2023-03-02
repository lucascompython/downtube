# This is Tauri App with NextJs that downloads (and or convert) Youtube videos

## Description

This is a Tauri App with a NextJs frontend that downloads and can convert Youtube videos.  
There are two versions of the app, one that has the [LOCAL](client/src-tauri-local/src/main.rs) dependencies that takes approximately 160mb of space and another that works with a [SERVER](client/src-tauri-server/src/main.rs) that has the dependencies, so no depencies in the client, approximately 3mb of space.

## Preview

![Preview](https://cdn.discordapp.com/attachments/626449728988774401/1077232713532186725/image.png)

## Build It

```bash
git clone https://github.com/lucascompython/downtube.git
cd downtube
./build.py -h
```

## TODO

- [ ] Update the UI with some more information about the video
- [ ] Add playlist support
- [ ] Maybe add mobile support with Tauri 2.0
