import { useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { open } from "@tauri-apps/api/dialog";
import Image from "next/image";
import githubLogo from "../assets/github.svg";
import {
    YoutubePlayer,
    EmptyPlayer,
} from "../components/YoutubePlayer/YoutubePlayer";

function App() {
    const [Msg, setMsg] = useState("");
    const [URL, setURL] = useState("");
    const [path, setPath] = useState("");
    const [audio, setAudio] = useState(false);

    async function DownloadVid() {
        if (!path) {
            setMsg("Please select a path!");
            return;
        }
        if (!URL) {
            setMsg("Please enter a URL!");
            return;
        }
        if (Msg === "Downloading...") return;

        setMsg("Downloading...");
        const info: any = await invoke("download", {
            url: URL,
            path: path,
            audio: audio,
        });
        console.log(info);
        setMsg(`Downloaded: ${info["title"]}`);
    }

    const DirPath = async () => {
        try {
            const selected = await open({
                multiple: false,
                directory: true,
            });
            if (typeof selected === "string") {
                setPath(selected);
                setMsg(`Path: ${selected}`);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const isAudio = () => {
        setAudio(!audio);
    };

    return (
        <div className="container">
            <h1>Downtube</h1>

            {URL.length === 43 ? (
                <YoutubePlayer vidId={URL.split("v=")[1]} />
            ) : (
                <EmptyPlayer />
            )}
            <div className="row">
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        DownloadVid();
                    }}
                >
                    <button type="button" onClick={DirPath}>
                        Path
                    </button>
                    <input
                        id="greet-input"
                        onChange={(e) => setURL(e.currentTarget.value)}
                        placeholder="Enter a Youtube URL..."
                    />
                    <button type="submit">Download</button>
                    <br />
                    <label htmlFor="audio">
                        Only Audio:
                        <input
                            className="checkbox"
                            type="checkbox"
                            name="audio"
                            onClick={isAudio}
                        />
                    </label>
                </form>
            </div>

            <p>{Msg}</p>

            <div className="row">
                <span className="logos">
                    <a
                        href="https://github.com/lucascompython/downtube"
                        target="_blank"
                    >
                        <Image
                            width={144}
                            height={144}
                            src={githubLogo}
                            className="logo next"
                            alt="Github logo"
                        />
                    </a>
                </span>
            </div>
        </div>
    );
}

export default App;
