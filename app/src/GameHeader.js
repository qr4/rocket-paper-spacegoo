import React, {useEffect, useState} from 'react';
import {BASE_URL} from "./Game";
import {Loading, Words, Link, withStyles} from "@arwes/arwes";
import {SoundWords} from "./components";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faScroll} from "@fortawesome/free-solid-svg-icons";

const styles = themes => {
    return {
        heading: {
            paddingLeft: themes.padding,
            paddingRight: themes.padding,
            marginTop: themes.margin / 2,
            display: "flex",
        },
        gameName: {
            flexGrow: "1"
        },
        opponents: {
            display: "flex",
            fontSize: "1.5em",
            marginBottom: themes.margin/2,
        },
        opponent: {
            width: "30%",
            display: "flex",
            justifyContent: "center",
            flexGrow: 1
        },
        vs: {
            width: "50px",
            textAlign: "center"
        }
    };
};

export const GameHeader = withStyles(styles)(({info, history, className, classes, show, arwesShow}) => {

    const [showContent, setShowContent] = useState(false);
    // Add a nice delay to between Heading and Content animation
    useEffect(
        () => {
            if (show && !showContent) {
                setTimeout(() => {
                    setShowContent && setShowContent(true);
                }, 2000);
            }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [show],
    );

    return info ?
        (
            <div className={className}>
                <div>
                    <span className={classes.heading}>
                        <span className={classes.gameName}>
                        <SoundWords animate layer='primary' show={show}>#</SoundWords>
                        <Link href="javascript:void(0)" onClick={() => history.push(`/game/${info["game_id"]}`)}>{`${info["game_id"]}`}</Link>
                            <span style={{padding:"10px"}}>&middot;</span>
                        <Link href={`${BASE_URL}/${info["game_log_name"]}`}>
                            <FontAwesomeIcon icon={faScroll} />
                        </Link>
                        </span>
                        {!info.finished && <Loading animate small className={classes.loadingElo}/> }
                    </span>
                    <div className={classes.opponents}>
                        <span className={classes.opponent}>
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player1"])}>
                                <Words animate layer='success' show={show}>{info['player1']}</Words>
                                {<sup>
                                    <Words layer={info.elodiff > 0 ? 'primary': 'secondary'} animate show={show && info.finished}>
                                        {(info.elodiff > 0 ? "+" : "") + Number(info.elodiff).toFixed(3)}
                                    </Words>
                                </sup>}
                                {" "}
                                <Words animate layer='primary' show={show}>{`(rank #${info["rank1"]})`}</Words>
                            </Link>
                        </span>
                        <Words layer='primary' className={classes.vs} animate show={showContent}>vs</Words>
                        <span className={classes.opponent}>
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player2"])}>
                                <Words animate layer='alert' show={show}>{info['player2']}</Words>
                                {<sup>
                                    <Words layer={-info.elodiff > 0 ? 'primary': 'secondary'} animate show={show && info.finished}>
                                        {(-info.elodiff > 0 ? "+" : "") + Number(-info.elodiff).toFixed(3)}
                                    </Words>
                                </sup>}
                                {" "}
                                <Words animate layer='primary' show={show}>{`(rank #${info["rank2"]})`}</Words>
                            </Link>
                        </span>
                    </div>
                </div>


            </div>
        ) :
        arwesShow && <Loading animate/> || null
});