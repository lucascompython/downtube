#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::Deserialize;
use serde_json::Value;
use std::collections::HashMap;
use std::io::Write;
use tauri::async_runtime::Mutex;

#[derive(Deserialize)]
struct DislikesResponse {
    dislikes: u32,
}

struct IPState(Mutex<String>);

struct InfoState(Mutex<HashMap<String, Value>>);

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

async fn extract_info(vid_id: &str, ip: String) -> Result<HashMap<String, Value>, reqwest::Error> {
    let url = ip + "/info?vid_id=" + vid_id;
    let url = url.replace('"', ""); // probably better way to do this

    let resp = reqwest::get(url)
        .await?
        .json::<HashMap<String, Value>>()
        .await?;

    Ok(resp)
}

#[tauri::command]
async fn get_info(
    handle: tauri::AppHandle,
    url: &str,
    ip_state: tauri::State<'_, IPState>,
    info_state: tauri::State<'_, InfoState>,
) -> Result<HashMap<String, Value>, ()> {
    let mut ip_state = ip_state.0.lock().await;
    let mut info_state = info_state.0.lock().await;

    if ip_state.is_empty() {
        *ip_state = get_ip(handle);
    }
    let vid_id = url.split("v=").collect::<Vec<&str>>()[1];

    let ip = ip_state.clone();

    let (info, dislikes) = tokio::join!(extract_info(vid_id, ip), get_dislikes(vid_id));
    let mut info = info.unwrap();
    info.insert(
        "dislike_count".to_string(),
        Value::String(dislikes.unwrap()),
    );

    *info_state = info.clone();

    Ok(info)
}

fn get_ip(handle: tauri::AppHandle) -> String {
    let settings_path = handle
        .path_resolver()
        .resolve_resource("./appsettings.json")
        .expect("Failed to resolve resource path");

    let file = std::fs::File::open(&settings_path).expect("Failed to open resource file");
    let appsettings: serde_json::Value =
        serde_json::from_reader(file).expect("Failed to read resource file");
    let ip = appsettings.get("ip").unwrap();

    ip.to_string()
}

#[tauri::command]
async fn download(
    url: &str,
    path: &str,
    audio: bool,
    info_state: tauri::State<'_, InfoState>,
    ip_state: tauri::State<'_, IPState>,
) -> Result<(), ()> {
    let vid_id = url.split("v=").collect::<Vec<&str>>()[1];

    let file_name = info_state.0.lock().await;
    let file_name = file_name.get("title").unwrap().as_str().unwrap();

    let ip = ip_state.0.lock().await;

    let url = ip.to_string() + "/download?vid_id=" + vid_id + "&audio=" + &audio.to_string();
    let url = url.replace('"', ""); // probably better way to do this
    let resp = reqwest::get(url).await.unwrap().bytes().await.unwrap();
    //save file
    let ext = if audio { ".mp3" } else { ".mp4" };
    let mut file = std::fs::File::create(path.to_string() + "/" + file_name + ext)
        .expect("Failed to create file");
    file.write_all(&resp).expect("Failed to write to file");

    Ok(())
}

#[tokio::main]
async fn main() {
    tauri::Builder::default()
        .manage(IPState(Default::default()))
        .manage(InfoState(Default::default()))
        .invoke_handler(tauri::generate_handler![download, get_info])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
