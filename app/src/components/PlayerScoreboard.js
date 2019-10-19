import {Heading, Link, Loading, Table, Words, withStyles} from '@arwes/arwes';
import {useHistory} from 'react-router-dom';
import React, {memo, useRef, useState} from 'react';

import {useInterval} from '../hooks/useInterval';

const styles = themes => ({
    firstPlace: {
        textTransform: 'uppercase',
    },
});

export const PlayerScoreboard = withStyles(styles)(
    memo(({title, show, scoreboardData, classes, isGlobalRanking}) => {
        const history = useHistory();
        const [displayedTableItems, setDisplayedTableItems] = useState(0);
        const refDisplayedTableItems = useRef(0);
        useInterval(() => {
            if (
                scoreboardData &&
                refDisplayedTableItems.current < scoreboardData.length
            ) {
                setDisplayedTableItems(refDisplayedTableItems.current + 1);
                refDisplayedTableItems.current =
                    refDisplayedTableItems.current + 1;
            }
        }, show ? 100 : null);

        return (
            <>
                <Heading node={'h3'}>{title}</Heading>
                {show && (scoreboardData ? (
                    <Table
                        animate
                        headers={[]}
                        dataset={scoreboardData.map((entry, index) => [
                            index,
                            <Link
                                onClick={() =>
                                    history.push(`/player/${entry[0]}`)
                                }>
                                <Words
                                    animate
                                    layer={
                                        entry[2] ? 'secondary':
                                        isGlobalRanking && index < 3
                                            ? 'success' : 'primary'
                                    }
                                    className={
                                        isGlobalRanking && index === 0
                                            ? classes.firstPlace
                                            : ''
                                    }
                                    show={show && displayedTableItems > index}>
                                    {entry[0]}
                                </Words>
                            </Link>,

                            entry[1].toFixed(3),
                        ])}
                    />
                ) : (
                    <Loading />
                ))}
            </>
        );
    }),
);
