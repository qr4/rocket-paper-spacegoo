import React from 'react';
import {BASE_URL} from "./Game";
import {Loading, Words, Link} from "@arwes/arwes";

export const GameHeader = ({info, history}) => {
    return info ?
        <>
            <div style={{textTransform: "initial"}}>
                <Words animate layer='primary'>Game #</Words>
                <Link href="javascript:void(0)" onClick={() => history.push(`/game/${info["game_id"]}`)}>{info["game_id"]}</Link>:&nbsp;
                <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player1"])}>
                    <Words animate layer='success'>{info['player1']}</Words>
                </Link>
                {" "}<sub>vs</sub>{" "}
                <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player2"])}>
                    <Words animate layer='alert'>{info['player2']}</Words>
                </Link>
                {" "}
                <Words layer='primary'>{!info.finished ?
                    <span>{(info.elodiff > 0 ? "+" : "") + Number(info.elodiff).toFixed(3)}</span> :
                    <Loading animate small/>
                }
                </Words>
            </div>
            <p style={{textTransform: "initial", fontWeight: "400"}}>
                <Words animate layer='primary'>
                    {`${info["player1"]} currently has rank #${info["rank1"]}, ${info["player2"]} currently has rank #${info["rank2"]}`}
                </Words>
                <Link href={`${BASE_URL}/${info["game_log_name"]}`}>{" "}{" "}raw gamelog</Link>
            </p>
        </>:
        <Loading animate/>
};
