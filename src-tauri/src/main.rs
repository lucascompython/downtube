#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use youtube_dl::YoutubeDl;

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
#[tauri::command]
async fn download(url: &str, path: &str, audio: bool) -> Result<String, ()> {
    //let yt_dlp_path = download_yt_dlp(".").await?;

    //let output = YoutubeDl::new("https://www.youtube.com/watch?v=VFbhKZFzbzk")
    //.youtube_dl_path(yt_dlp_path)
    //.run_async()
    //.await?;
    println!("antes do output");
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
        let title = output.unwrap().into_single_video().unwrap().title;

        Ok(title)
    } else {
        let output = YoutubeDl::new(url)
            .download(true)
            .output_directory(path)
            .format("bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio")
            .extra_arg("--merge-output-format")
            .extra_arg("mp4")
            .run_async()
            .await;
        let title = output.unwrap().into_single_video().unwrap().title;

        Ok(title)
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
