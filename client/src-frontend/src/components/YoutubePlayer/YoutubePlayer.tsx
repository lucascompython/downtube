import styles from "./YoutubePlayer.module.css";

export const YoutubePlayer = ({ vidId }: { vidId: string }) => {
    return (
        <div>
            <iframe
                width="560"
                height="315"
                src={`https://www.youtube.com/embed/${vidId}`}
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                style={{ border: "0px" }}
            ></iframe>
        </div>
    );
};

export const EmptyPlayer = () => {
    return (
        <div className={styles.empty}>
            <h1>Search for a video</h1>
        </div>
    );
};
