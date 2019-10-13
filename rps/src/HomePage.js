import {
    Col,
    Frame,
    Heading,
    Link,
    Loading,
    Row,
    withStyles,
} from '@arwes/arwes';
import {useDebounce} from 'use-debounce';
import {useHistory} from 'react-router-dom';
import React, {useEffect, useState, useCallback} from 'react';

import {BASE_URL} from './Game';
import {PageWrapper} from './components/PageWrapper';
import {PlayerScoreboard} from './components/PlayerScoreboard';
import {RecentGames} from './components/RecentGames';
import {SoundWords} from './components';
import {useInterval} from './hooks/useInterval';

const styles = theme => ({
    frameContent: {
        padding: theme.padding,
    },

    recentGamesContainer: {
        display: 'flex',
    },
    title: {flexGrow: 1},
    latestLink: {
        textTransform: 'initial',
    },
});

const HomePageRecentGamesTitle = ({classes}) => {
    const history = useHistory();
    return (
        <div className={classes.recentGamesContainer}>
            <div className={classes.title}>Recent games</div>
            <div>
                <Link
                    onClick={() => history.push(`/game/latest`)}
                    className={classes.latestLink}>
                    <SoundWords animate show={true}>
                        Watch latest
                    </SoundWords>
                </Link>
            </div>
        </div>
    );
};

const HomePageFrameContent = ({show, classes, gameData}) => {
    // Smoother animations
    const [delayedShow] = useDebounce(show, 200);
    const [delayedShow2] = useDebounce(show, 400);
    return (
        <div className={classes.frameContent}>
            <p>
                <SoundWords animate show={show}>
                    Total of
                </SoundWords>{' '}
                {gameData ? (
                    <SoundWords animate show={show}>
                        {gameData.num_games.toString()}
                    </SoundWords>
                ) : (
                    show && <Loading small />
                )}{' '}
                <SoundWords animate show={show}>
                    games played.
                </SoundWords>
            </p>
            <Row>
                <Col s={12} m={12} l={6}>
                    <PlayerScoreboard
                        isGlobalRanking
                        title={'Top 40'}
                        show={delayedShow}
                        scoreboardData={gameData ? gameData.highscores : null}
                    />
                </Col>
                <Col s={12} m={12} l={6}>
                    <RecentGames
                        title={<HomePageRecentGamesTitle classes={classes} />}
                        show={delayedShow2}
                        lastGamesData={gameData ? gameData.last_games : null}
                    />
                </Col>
            </Row>
        </div>
    );
};

export const HomePage = withStyles(styles)(({show, classes}) => {
    const [gameData, setGameData] = useState(null);
    const loadData = useCallback(async () => {
        const data = await fetch(`${BASE_URL}/info.json`);
        const json = await data.json();
        setGameData(json);
    }, []);
    useInterval(loadData, gameData && gameData.finished ? null : 2500);
    useEffect(
        () => {
            setGameData(null);
            loadData();
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [],
    );

    return (
        <PageWrapper>
            <Heading node="h1">
                <SoundWords animate show={show}>
                    Rocket Scissor Spacegoo
                </SoundWords>
            </Heading>
            <Frame animate show={show} layer="primary" corners={5} level={3}>
                {anim => (
                    <HomePageFrameContent
                        show={anim.entered}
                        gameData={gameData}
                        classes={classes}
                    />
                )}
            </Frame>
        </PageWrapper>
    );
});
