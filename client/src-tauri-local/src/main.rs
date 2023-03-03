#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::Deserialize;
use std::collections::HashMap;
use std::env::consts::OS;
use std::process::Command;
use youtube_dl::YoutubeDl;

#[derive(Deserialize)]
struct DislikesResponse {
    dislikes: u32,
}

async fn get_dislikes(vid_id: &str) -> Result<String, reqwest::Error> {
    let resp = reqwest::get(format!(
        "https://returnyoutubedislikeapi.com/votes?videoId={}",
        vid_id
    ))
    .await?
    .json::<DislikesResponse>()
    .await?;
    Ok(resp.dislikes.to_string())
}

async fn get_video(
    url: &str,
    path: &str,
    audio: bool,
) -> Result<HashMap<&'static str, String>, ()> {
    let mut output = YoutubeDl::new(url);

    let mut output = output
        .download(true)
        .output_directory(path)
        .output_template("%(title)s.%(ext)s");
    if audio {
        output = output
            .extract_audio(true)
            .extra_arg("--audio-format")
            .extra_arg("mp3");
    } else {
        output = output
            .format("bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio")
            .extra_arg("--merge-output-format")
            .extra_arg("mp4");
    }

    if OS == "windows" {
        output = output.youtube_dl_path("yt-dlp.exe");
    } else if OS == "macos" {
        output = output.youtube_dl_path("yt-dlp_macos");
    }
    let output = output.run_async().await;

    let mut info_map = HashMap::new();

    //TODO: update UI and show all this info
    let info = output.unwrap().into_single_video().unwrap();
    info_map.insert("title", info.title);
    info_map.insert("upload_date", info.upload_date.unwrap());
    info_map.insert("thumbnail", info.thumbnail.unwrap());
    info_map.insert("duration", info.duration.unwrap().to_string());
    info_map.insert("uploader", info.uploader.unwrap());
    info_map.insert("uploader_url", info.uploader_url.unwrap());
    info_map.insert("view_count", info.view_count.unwrap().to_string());
    info_map.insert("like_count", info.like_count.unwrap().to_string());

    Ok(info_map)
}

#[tauri::command]
async fn download(url: &str, path: &str, audio: bool) -> Result<HashMap<&'static str, String>, ()> {
    let vid_id = url.split("v=").collect::<Vec<&str>>()[1];
    let (info, dislikes) = tokio::join!(get_video(url, path, audio), get_dislikes(vid_id));

    let mut info_map = info.unwrap();
    info_map.insert("dislike_count", dislikes.unwrap());

    Ok(info_map)
}

#[tokio::main]
async fn main() {
    if OS == "linux" {
        Command::new("pip3")
            .arg("install")
            .arg("yt-dlp")
            .output()
            .expect("failed to install yt-dlp");
    }

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![download])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
