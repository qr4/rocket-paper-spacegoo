import React, {memo} from 'react';

import {Loading} from '@arwes/arwes';
import {VictoryCursorContainer, VictoryChart, VictoryTheme, VictoryLine} from "victory";

export const GameGraph = memo(({game, turn, dispatch, show, arwesShow}) => {
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
    if (game) {
        for (let idx = 0; idx < game.length; idx++) {
            const round = game[idx];
            const fleets = [0, 0, 0];
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
    }

    const theme = VictoryTheme.material;
    theme.axis.style.axis.stroke = "#8bebfe";
    theme.axis.style.tickLabels.fill = "#8bebfe";
    theme.axis.style.grid.stroke = "#ccc";


    return (
        show && game ?
            <VictoryChart theme={VictoryTheme.material} width={1200}
                          containerComponent={
                              <VictoryCursorContainer cursorLabelComponent={<div style={{display: "none"}} />}
                                                      cursorDimension="x"
                                                      onCursorChange={d => d && dispatch({type: 'setMove', value: Math.ceil(d)})} />
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
            :
            arwesShow && <Loading animate/> || null
    );
});