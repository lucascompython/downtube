import styles from "./ShowInfo.module.css";

function numberWithCommas(x: number): string {
    if (x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    return "N/A";
}

const ShowInfo = ({ info }: any) => {
    if (Object.keys(info).length === 0)
        return (
            <div>
                <div className={styles.container}>
                    <div className={styles.containerLeft}>
                        <h2>Likes: N/A</h2>
                        <h2>Dislikes: N/A</h2>
                        <h2>Subscribers: N/A</h2>
                    </div>
                    <div className={styles.containerRight}>
                        <h2>Views: N/A</h2>
                        <h2>Comments: N/A</h2>
                        <h2>Upload date: N/A</h2>
                    </div>
                </div>
            </div>
        );

    let d = info["upload_date"];
    let date = d.slice(6, 8) + "/" + d.slice(4, 6) + "/" + d.slice(0, 4);
    return (
        <div className={styles.container}>
            <div className={styles.containerLeft}>
                <h2>Likes: {numberWithCommas(info["like_count"])}</h2>
                <h2>Dislikes: {numberWithCommas(info["dislike_count"])}</h2>
                <h2>
                    Subscribers:{" "}
                    {numberWithCommas(info["channel_follower_count"])}
                </h2>
            </div>
            <div className={styles.containerRight}>
                <h2>Views: {numberWithCommas(info["view_count"])}</h2>
                <h2>Comments: {numberWithCommas(info["comment_count"])}</h2>
                <h2>Upload date: {date}</h2>
            </div>
        </div>
    );
};

export default ShowInfo;
