import {Heading, Loading, Table, withStyles} from '@arwes/arwes';
import React, {memo, useRef, useState} from 'react';

import {SoundWords} from './';
import {useInterval} from '../hooks/useInterval';

const styles = theme => ({
    versusColumnEntry: {
        display: 'flex',
        justifyContent: 'space-evenly',
    },
});

export const RecentGames = withStyles(styles)(
    memo(({title, show, lastGamesData, classes}) => {
        const [displayedTableItems, setDisplayedTableItems] = useState(0);
        const refDisplayedTableItems = useRef(0);
        useInterval(() => {
            if (
                lastGamesData &&
                refDisplayedTableItems.current < lastGamesData.length
            ) {
                setDisplayedTableItems(refDisplayedTableItems.current + 1);
                refDisplayedTableItems.current =
                    refDisplayedTableItems.current + 1;
            }
        }, show ? 100 : null);

        return (
            <>
                <Heading node={'h3'}>{title}</Heading>
                {show && (lastGamesData ? (
                    <Table
                        animate
                        dataset={lastGamesData.map((entry, index) => [
                            entry.game_id,
                            <div className={classes.versusColumnEntry}>
                                <SoundWords
                                    layer="success"
                                    animate
                                    show={show && displayedTableItems > index}>
                                    {entry.player1}
                                </SoundWords>{' '}
                                <sub>
                                    <SoundWords
                                        layer="disabled"
                                        animate
                                        show={
                                            show && displayedTableItems > index
                                        }>
                                        vs
                                    </SoundWords>
                                </sub>{' '}
                                <SoundWords
                                    layer="alert"
                                    animate
                                    show={show && displayedTableItems > index}>
                                    {entry.player2}
                                </SoundWords>
                            </div>,
                            entry.elodiff > 0
                                ? `+${entry.elodiff.toFixed(3)}`
                                : entry.elodiff,
                        ])}
                    />
                ) : (
                    <Loading />
                ))}
            </>
        );
    }),
);
