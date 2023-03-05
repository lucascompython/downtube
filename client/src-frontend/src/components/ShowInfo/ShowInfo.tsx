import styles from "./ShowInfo.module.css";
const ShowInfo = ({ info }: any) => {
    if (Object.keys(info).length === 0) return <div></div>;
    let d = info["upload_date"];
    let date = d.slice(6, 8) + "/" + d.slice(4, 6) + "/" + d.slice(0, 4);
    return (
        <div className={styles.container}>
            <div className={styles.containerLeft}>
                <h2>Likes: {info["like_count"]}</h2>
                <h2>Dislikes: {info["dislike_count"]}</h2>
                <h2>Subscribers: {info["channel_follower_count"]}</h2>
            </div>
            <div className={styles.containerRight}>
                <h2>Views: {info["view_count"]}</h2>
                <h2>Comments: {info["comment_count"]}</h2>
                <h2>Upload date: {date}</h2>
            </div>
        </div>
    );
};

export default ShowInfo;
