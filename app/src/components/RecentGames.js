import {Heading, Link, Loading, withStyles} from '@arwes/arwes';
import {useHistory} from 'react-router-dom';
import React, { memo, useRef, useState } from 'react';

import {SoundWords} from './';
import {useInterval} from '../hooks/useInterval';
import Table from './Table';

const styles = theme =>
    console.info(theme.color) || {
        versusColumnEntry: {
            display: 'flex',
            justifyContent: 'space-evenly',
        },
        eloLost: {
            color: theme.color.secondary.light,
        },
    };

export const RecentGames = withStyles(styles)(
    memo(({title, show, lastGamesData, classes, focusedPlayer}) => {
        const history = useHistory();
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
                {show &&
                    (lastGamesData ? (
                        <Table
                            animate
                            dataset={lastGamesData.map(
                                (
                                    {game_id, player1, player2, elodiff},
                                    index,
                                ) => {
                                    const [
                                        leftPlayer,
                                        rightPlayer,
                                        elodelta,
                                    ] =
                                        !focusedPlayer ||
                                        focusedPlayer === player1
                                            ? [player1, player2, elodiff, false]
                                            : [
                                                  player2,
                                                  player1,
                                                  -elodiff,
                                              ];
                                    return {
                                        key: `${game_id}`,
                                        value: [
                                            <Link
                                                href="javascript:void(0)"
                                                onClick={() =>
                                                    history.push(
                                                        `/game/${game_id}`,
                                                    )
                                                }>
                                                {game_id}
                                            </Link>,
                                            <div
                                                className={
                                                    classes.versusColumnEntry
                                                }>
                                                <Link
                                                    href="javascript:void(0)"
                                                    onClick={() =>
                                                        history.push(
                                                            `/player/${leftPlayer}`,
                                                        )
                                                    }>
                                                    <SoundWords
                                                        layer={
                                                            leftPlayer === player1
                                                                ? 'success'
                                                                : 'alert'
                                                        }
                                                        animate
                                                        show={
                                                            show &&
                                                            displayedTableItems >
                                                                index
                                                        }>
                                                        {leftPlayer}
                                                    </SoundWords>
                                                </Link>{' '}
                                                <sub>
                                                    {show &&
                                                        displayedTableItems >
                                                            index &&
                                                        'vs'}
                                                </sub>{' '}
                                                <Link
                                                    href="javascript:void(0)"
                                                    onClick={() =>
                                                        history.push(
                                                            `/player/${rightPlayer}`,
                                                        )
                                                    }>
                                                    <SoundWords
                                                        layer={
                                                            rightPlayer === player1
                                                                ? 'success'
                                                                : 'alert'
                                                        }
                                                        animate
                                                        show={
                                                            show &&
                                                            displayedTableItems >
                                                                index
                                                        }>
                                                        {rightPlayer}
                                                    </SoundWords>
                                                </Link>
                                            </div>,
                                            <span
                                                className={
                                                    elodelta < 0 &&
                                                    classes.eloLost
                                                }>
                                                {elodelta
                                                    ? elodelta > 0
                                                      ? `+${elodelta.toFixed(
                                                            3,
                                                        )}`
                                                      : elodelta.toFixed(3)
                                                    : '---'}
                                            </span>,
                                        ],
                                    };
                                },
                            )}
                        />
                    ) : (
                        <Loading />
                    ))}
            </>
        );
    }),
);
