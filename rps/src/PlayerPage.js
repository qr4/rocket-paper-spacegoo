import {
    Col,
    Heading,
    Link,
    Project,
    Row,
    Table,
    Words,
    withStyles,
} from '@arwes/arwes';
import {useParams, useHistory} from 'react-router-dom';
import React, {useRef, useState, useEffect} from 'react';

import {PageWrapper} from './components/PageWrapper';
import {SoundWords} from './components';
import {useInterval} from './hooks/useInterval';

const testData = {
    highscore_first: 0,
    highscores: [
        ['random_bot', 25.0, false],
        ['ur mum lul', -30.0, false],
        ['1337Hackorz', -30.0, false],
        ['The bigger threat', 2034.123987123, false],
    ],
    last_games: [
        {
            elodiff: 5.0,
            game_id: '224',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '224',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '223',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '223',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '222',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '222',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '221',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '221',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '220',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '220',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '219',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '219',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '218',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '218',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '217',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '217',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '216',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '216',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '215',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '215',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '214',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '214',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '213',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '213',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '212',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '212',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '211',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '211',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '210',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '210',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '209',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '209',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '208',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '208',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '207',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '207',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '206',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '206',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '205',
            player1: 'random_bot',
            player2: 'random_bot',
        },
        {
            elodiff: 5.0,
            game_id: '205',
            player1: 'random_bot',
            player2: 'random_bot',
        },
    ],
    num_games: 448,
    rank: 1,
    username: 'random_bot',
};

const styles = theme => ({
    versusColumnEntry: {
        display: 'flex',
        justifyContent: 'space-evenly',
    },
    summary: {
        marginBottom: theme.margin,
    },
});

export const PlayerPage = withStyles(styles)(({show, classes}) => {
    const history = useHistory();
    const [showContent, setShowContent] = useState(false);
    // Add a nice delay to between Heading and Content animation
    useEffect(
        () => {
            if (show && !showContent) {
                setTimeout(() => {
                    setShowContent && setShowContent(true);
                }, 1000);
            }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [show],
    );

    const [displayedTableItems, setDisplayedTableItems] = useState(0);
    const refDisplayedTableItems = useRef(0);
    useInterval(() => {
        if (
            testData &&
            testData.last_games &&
            refDisplayedTableItems.current < testData.last_games.length
        ) {
            setDisplayedTableItems(refDisplayedTableItems.current + 1);
            refDisplayedTableItems.current = refDisplayedTableItems.current + 1;
        }
    }, show ? 100 : null);

    const {playerName} = useParams();
    const playerData = testData;
    return (
        <PageWrapper>
            <Project show={show} animate header={playerName}>
                {anim => (
                    <>
                        <div className={classes.summary}>
                            <SoundWords animate show={anim.entered}>
                                {`Total of ${playerData.num_games} played.`}
                            </SoundWords>{' '}
                            <SoundWords animate show={anim.entered}>
                                Ranked
                            </SoundWords>{' '}
                            <SoundWords
                                animate
                                show={showContent}
                                layer={playerData.rank <= 3 ? 'success' : null}>
                                {`#${
                                    playerData.rank
                                        ? playerData.rank.toString()
                                        : ''
                                }.`}
                            </SoundWords>{' '}
                            <SoundWords animate show={anim.entered}>
                                View
                            </SoundWords>{' '}
                            <Link
                                onClick={() =>
                                    history.push(
                                        `/player/${playerData.username}/live`,
                                    )
                                }>
                                <SoundWords animate show={anim.entered}>
                                    {`${playerData.username}'s games`}
                                </SoundWords>
                            </Link>{' '}
                            <SoundWords animate show={anim.entered}>
                                live.
                            </SoundWords>
                        </div>
                        <Row>
                            <Col s={12} m={12} l={6}>
                                <Heading node={'h3'}>
                                    {`${playerData.username}'s scoreboard`}
                                </Heading>
                                <Table
                                    animate
                                    headers={[]}
                                    dataset={testData.highscores.map(
                                        (entry, index) => [
                                            index,

                                            <Link
                                                onClick={() =>
                                                    history.push(
                                                        `/player/${
                                                            playerData.username
                                                        }/live`,
                                                    )
                                                }>
                                                <Words
                                                    animate
                                                    show={
                                                        anim.entered &&
                                                        displayedTableItems >
                                                            index
                                                    }
                                                    >
                                                    {entry[0]}
                                                </Words>
                                            </Link>,

                                            entry[1],
                                        ],
                                    )}
                                />
                            </Col>
                            <Col s={12} m={12} l={6}>
                                <Heading node={'h3'}>
                                    {`${playerData.username}'s recent games`}
                                </Heading>
                                <Table
                                    animate
                                    dataset={testData.last_games.map(
                                        (entry, index) => [
                                            entry.game_id,
                                            anim.entered && (
                                                <div
                                                    className={
                                                        classes.versusColumnEntry
                                                    }>
                                                    <SoundWords
                                                        layer="success"
                                                        animate
                                                        show={
                                                            anim.entered &&
                                                            displayedTableItems >
                                                                index
                                                        }>
                                                        {entry.player1}
                                                    </SoundWords>{' '}
                                                    <sub>
                                                        <SoundWords
                                                            layer="disabled"
                                                            animate
                                                            show={
                                                                anim.entered &&
                                                                displayedTableItems >
                                                                    index
                                                            }>
                                                            vs
                                                        </SoundWords>
                                                    </sub>{' '}
                                                    <SoundWords
                                                        layer="alert"
                                                        animate
                                                        show={
                                                            anim.entered &&
                                                            displayedTableItems >
                                                                index
                                                        }>
                                                        {entry.player1}
                                                    </SoundWords>
                                                </div>
                                            ),
                                            entry.elodiff,
                                        ],
                                    )}
                                />
                            </Col>
                        </Row>
                    </>
                )}
            </Project>
        </PageWrapper>
    );
});
