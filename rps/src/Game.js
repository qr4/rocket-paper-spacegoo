import React, {useState, useEffect, useReducer} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {
    faChevronLeft,
    faChevronRight,
    faPlay,
    faPauseCircle
} from '@fortawesome/free-solid-svg-icons';
import {VictoryCursorContainer, VictoryChart, VictoryTheme, VictoryLine} from "victory";

import {Button, Loading, Project, Words, Link, withStyles } from "@arwes/arwes";
import { game } from "./dummy_data";
import {Container} from "./components/container";
import {useHistory, useParams} from "react-router";
import {useInterval} from "./hooks/useInterval";


const BASE_URL = "http://localhost:8080";

const styles = themes => {
    console.log(themes);
    return {
        cursorLabel: {
            display: "none"
        },
        heading: {
            textTransform: "unset !important",
            "@global": {
                "h1": {
                    width:"100%",
                    "@global": {
                        span: {
                            width: "100%",
                        }
                    }
                }
            },
            width: "100%",
        },
        headingLoader: {
           margin: 0
        },

        controls: {
            display: "flex",
            justifyContent: "center",
            marginTop: themes.margin
        },

        controlElements: {
            marginLeft: themes.margin,
            marginRight: themes.margin,
            cursor: "pointer"
        }

    };
};

const reducer = (state, action) => {
    switch (action.type) {
        case 'incrementMove':
            return {...state, turn: Math.min(game.length, state.turn + 1)};
        case 'decrementMove':
            return {...state, turn: Math.max(0, state.turn - 1)};
        case 'setMove':
            return {...state, turn: action.value};
        case 'togglePlayback': {
            return {...state, playback: !state.playback};
        }
        default:
            throw Error();
    }
};

export const Game = withStyles(styles)(({show, classes}) => {
    const {id} = useParams();
    const [{turn, playback}, dispatch] = useReducer(reducer, {turn: 0, playback: false});
    const history = useHistory();
    const [animateTurn, setAnimateTurn] = useState(true);
    const [info, setInfo] = useState(undefined);

    useEffect(() => {
        setAnimateTurn(false);
    });

    useInterval(async () => {
        const data = await fetch(`${BASE_URL}/game/${id}/info.json`);
        const json = await data.json();
        setInfo(json);
    }, 1000);

    useInterval(() => playback && dispatch({type: 'increment'}), 10);

    const data = [{
        label: 'neutral',
        color: '#ccc',
        data: []
    }, {
        label: 'player1',
        color: '#6f6',
        data: []
    }, {
        label: 'player2',
        color: '#f66',
        data: []
    }];

    let maxY = 0;
    for (let idx = 0; idx < game.length; idx++) {
        const round = game[idx];
        const fleets = [0,0,0];
        for (let fi = 0; fi < round.fleets.length; fi++) {
            const fleet = round.fleets[fi];
            fleets[fleet.owner_id] += fleet.ships[0] + fleet.ships[1] + fleet.ships[2];
        }
        for (let pi = 0; pi < round.planets.length; pi++) {
            const planet = round.planets[pi];
            fleets[planet.owner_id] += planet.ships[0] + planet.ships[1] + planet.ships[2];
        }
        for (let player_id = 0; player_id <= 2; player_id++) {
            data[player_id].data.push({x: idx, y: fleets[player_id]});
            maxY = Math.max(maxY, fleets[player_id]);
        }
    }

    const theme = VictoryTheme.material;
    theme.axis.style.axis.stroke = "#8bebfe";
    theme.axis.style.tickLabels.fill = "#8bebfe";
    theme.axis.style.grid.stroke = "#ccc";

    return (
        <Container>
            <Project
                show={show}
                className={!info && classes.heading}
                header={info ?
                    <>
                        <div>
                            <span>Game #</span>
                            <Link href="javascript:void(0)" onClick={() => history.push("/game/" + id)}>{id}</Link>:&nbsp;
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player1"])}>
                                <Words animate layer='success'>{game[0].players[0].name}</Words>
                            </Link>
                            {" "}<sub>vs</sub>{" "}
                            <Link href="javascript:void(0)" onClick={() => history.push("/player/" + info["player2"])}>
                                <Words animate layer='alert'>{game[0].players[1].name}</Words>
                            </Link>
                        </div>
                        <p style={{textTransform: "initial", fontWeight: "400"}}>
                            <Words animate layer='primary'>
                                {`${info["player1"]} currently has rank #${info["rank1"]}, ${info["player2"]} currently has rank #${info["rank2"]}`}
                            </Words>
                            <Link href={`${BASE_URL}/${info["game_log_name"]}`}>&nbsp;&nbsp;raw gamelog</Link>
                        </p>
                    </>:
                    <Loading animate className={classes.headingLoader}/>}>

                <div className={classes.controls}>
                    <Button animate layer='primary' onClick={() => dispatch({type: 'decrement'})}><FontAwesomeIcon className={classes.controlElements} icon={faChevronLeft} size="lg"/></Button>
                    <Button animate layer='primary' onClick={() => setPlay(!playback)}>
                        <FontAwesomeIcon fixedWidth className={classes.controlElements} icon={playback ? faPauseCircle : faPlay} size="lg"/>
                    </Button>
                    <Button animate layer='primary' onClick={() => dispatch({type: 'increment'})}><FontAwesomeIcon className={classes.controlElements} icon={faChevronRight} size="lg"/></Button>
                </div>
                <VictoryChart theme={VictoryTheme.material} width={1200}
                              containerComponent={
                                  <VictoryCursorContainer cursorLabelComponent={<div className={classes.style} />}
                                                          cursorDimension="x"
                                                          onCursorChange={d => d && dispatch(Math.floor(d))} />
                              }>
                    {data.map((d, idx) =>
                        (<VictoryLine
                            style={{ data: { stroke: d.color } }}
                            data={d.data}
                            key={idx}
                        />))}
                    <VictoryLine
                        style={{data: { stroke: "#8bebfe", strokeWidth: "4px"}}}
                        data={[{x:turn, y:0}, {x:turn, y: maxY}]}
                    />
                </VictoryChart>

                <Words animate={animateTurn}>{"Current turn " + turn}</Words>

            </Project>
        </Container>
    );
});
