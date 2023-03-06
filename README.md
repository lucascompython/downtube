# This is Tauri App with NextJs that downloads (and or convert) Youtube videos

## Description
<div align="center">
    <img src="https://cdn.discordapp.com/attachments/795277227423301643/1082380938446639127/downtubenovo.png" height="100" width="100"/>  
</div>

There are two versions of the app, one that has the [LOCAL](client/src-tauri-local/src/main.rs) dependencies that takes approximately 160mb of space and another that works with a [SERVER](client/src-tauri-server/src/main.rs) that has the dependencies, so no depencies in the client, approximately 3mb of space.  
The [server](server/main.py) was only tested on Linux, but it should work on Windows and Mac too.  
Didn't test anything on Mac.

## Preview

![Preview](https://cdn.discordapp.com/attachments/626449728988774401/1081980411577651380/image.png)

## Build It

```bash
git clone https://github.com/lucascompython/downtube.git
cd downtube
python3 build.py -h
```

## TODO

- [X] Update the UI with some more information about the video
- [ ] Add playlist support
- [ ] Maybe add mobile support with Tauri 2.0
