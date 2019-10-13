import React from 'react';
import {BASE_URL} from "./Game";
import {Loading, Words, Link, withStyles} from "@arwes/arwes";
import {SoundWords} from "./components";

const styles = themes => {
    return {
        heading: {
            display: "flex",
        },
        gameName: {
            flexGrow: "1"
        },
        loadingElo: {
            marginRight: themes.margin
        }
    };
};

export const GameHeader = withStyles(styles)(({info, history, className, classes, show, arwesShow}) => {
    return info ?
        (
            <div className={className}>
                <div>
                    <h2 className={classes.heading}>
                        <span className={classes.gameName}>
                            <SoundWords animate layer='primary' show={show}>Game #</SoundWords>
                            <Link href="javascript:void(0)" onClick={() => history.push(`/game/${info["game_id"]}`)}>{info["game_id"]}</Link>:&nbsp;
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player1"])}>
                                <Words animate layer='success' show={show}>{info['player1']}</Words>
                            </Link>
                            {" "}<sub>vs</sub>{" "}
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player2"])}>
                                <Words animate layer='alert' show={show}>{info['player2']}</Words>
                            </Link>
                            {" "}
                            {info.finished &&
                            <span style={{marginLeft: "40px"}}>
                                {"Elo diff: "}
                                <Words animate layer='success' show={show}>{info['player1']}</Words>
                                {" "}
                                <Words layer={info.elodiff > 0 ? 'primary': 'secondary'}>
                                    {(info.elodiff > 0 ? "+" : "") + Number(info.elodiff).toFixed(3)}
                                </Words>
                                {", "}
                                 <Words animate layer='alert' show={show}>{info['player2']}</Words>
                                {" "}
                                <Words layer={-info.elodiff > 0 ? 'primary': 'secondary'}>
                                    {(-info.elodiff > 0 ? "+" : "") + Number(-info.elodiff).toFixed(3)}
                                </Words>
                            </span>
                            }
                        </span>
                        {!info.finished && <Loading animate small className={classes.loadingElo}/> }
                    </h2>
                </div>
                <p>
                    <Words animate layer='primary' show={show}>
                        {`${info["player1"]} currently has rank`}
                    </Words>
                    {" "}
                    <b>
                        <Words animate layer={info["rank1"] <= 3 ? 'success' : 'primary'} show={show}>
                            {`#${info["rank1"]}`}
                        </Words>
                    </b>
                    <Words animate layer='primary' show={show}>
                        {`, ${info["player2"]} currently has rank`}
                    </Words>
                    {" "}
                    <b>
                        <Words animate layer={info["rank2"] <= 3 ? 'success' : 'primary'} show={show}>
                            {`#${info["rank2"]}`}
                        </Words>
                    </b>
                    <Link href={`${BASE_URL}/${info["game_log_name"]}`} style={{marginLeft: "20px"}}>
                        <Words animate show={show}>raw gamelog</Words>
                    </Link>
                </p>
            </div>
        ) :
        arwesShow && <Loading animate/> || null
});