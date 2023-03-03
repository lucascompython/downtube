#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::Deserialize;
use serde_json::Value;
use std::collections::HashMap;
use std::fs::rename;
use std::io::Write;
use std::path::Path;

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

async fn get_file(vid_id: &str, ip: &str, audio: bool, path: &str) -> Result<(), reqwest::Error> {
    let url = ip.to_string() + "/download?vid_id=" + vid_id + "&audio=" + &audio.to_string();
    let resp = reqwest::get(url).await?.bytes().await?;
    //save file
    let ext = if audio { ".mp3" } else { ".mp4" };
    let mut file = std::fs::File::create(path.to_string() + "/.temp" + vid_id + ext)
        .expect("Failed to create file");
    file.write_all(&resp).expect("Failed to write to file");

    Ok(())
}

async fn get_info(
    vid_id: &str,
    ip: &str,
    audio: bool,
) -> Result<HashMap<String, Value>, reqwest::Error> {
    let url = ip.to_string() + "/info?vid_id=" + vid_id + "&audio=" + &audio.to_string();

    let resp = reqwest::get(url)
        .await?
        .json::<HashMap<String, Value>>()
        .await?;

    Ok(resp)
}

fn rename_file(path: &str, name: &str, audio: bool, vid_id: &str) {
    let ext = if audio { ".mp3" } else { ".mp4" };
    let temp_path = Path::new(path).join(".temp".to_owned() + vid_id + ext);
    let name = name.replace('"', "");
    let new_path = Path::new(path).join(name.to_owned() + ext);
    rename(
        temp_path,
        new_path
    )
    .expect("Failed to rename file");
}

#[tauri::command]
async fn download(
    handle: tauri::AppHandle,
    url: &str,
    path: &str,
    audio: bool,
) -> Result<HashMap<String, Value>, ()> {
    let settings_path = handle
        .path_resolver()
        .resolve_resource("./appsettings.json")
        .expect("Failed to resolve resource path");

    let vid_id = url.split("v=").collect::<Vec<&str>>()[1];

    let file = std::fs::File::open(&settings_path).expect("Failed to open resource file");
    let appsettings: serde_json::Value =
        serde_json::from_reader(file).expect("Failed to read resource file");
    let ip = appsettings.get("ip").unwrap();

    let (dislikes, _) = tokio::join!(
        get_dislikes(vid_id),
        get_file(vid_id, ip.as_str().unwrap(), audio, path)
    );

    let dislikes = dislikes.unwrap();

    let mut info = get_info(vid_id, ip.as_str().unwrap(), audio).await.unwrap();
    rename_file(
        path,
        info.get("title").unwrap().to_string().as_str(),
        audio,
        vid_id,
    );
    info.insert("dislikes".to_string(), dislikes.into());

    Ok(info)
}

#[tokio::main]
async fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![download])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
