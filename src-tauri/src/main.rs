#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::collections::HashMap;
use youtube_dl::YoutubeDl;

#[tauri::command]
async fn download(url: &str, path: &str, audio: bool) -> Result<HashMap<&'static str, String>, ()> {
    //TODO find a way to code this better
    if audio {
        let output = YoutubeDl::new(url)
            .download(true)
            .output_directory(path)
            .extract_audio(true)
            .extra_arg("--audio-format")
            .extra_arg("mp3")
            .run_async()
            .await;
        let mut info_map = HashMap::new();

        let info = output.unwrap().into_single_video().unwrap();
        info_map.insert("title", info.title);
        info_map.insert("upload_date", info.upload_date.unwrap());
        info_map.insert("thumbnail", info.thumbnail.unwrap());
        info_map.insert("duration", info.duration.unwrap().to_string());
        info_map.insert("uploader", info.uploader.unwrap());
        info_map.insert("uploader_url", info.uploader_url.unwrap());
        info_map.insert("view_count", info.view_count.unwrap().to_string());
        info_map.insert("like_count", info.like_count.unwrap().to_string());
        //info_map.insert("dislike_count", info.dislike_count.unwrap().to_string());

        Ok(info_map)
    } else {
        let output = YoutubeDl::new(url)
            .download(true)
            .output_directory(path)
            .format("bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio")
            .extra_arg("--merge-output-format")
            .extra_arg("mp4")
            .run_async()
            .await;
        let mut info_map = HashMap::new();

        let info = output.unwrap().into_single_video().unwrap();
        info_map.insert("title", info.title);
        info_map.insert("upload_date", info.upload_date.unwrap());
        info_map.insert("thumbnail", info.thumbnail.unwrap());
        info_map.insert("duration", info.duration.unwrap().to_string());
        info_map.insert("uploader", info.uploader.unwrap());
        info_map.insert("uploader_url", info.uploader_url.unwrap());
        info_map.insert("view_count", info.view_count.unwrap().to_string());
        info_map.insert("like_count", info.like_count.unwrap().to_string());
        //info_map.insert("dislike_count", info.dislike_count.unwrap().to_string());

        Ok(info_map)
    }

    //println!("Video title: {}", title);
}

#[tokio::main]
async fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![download])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
