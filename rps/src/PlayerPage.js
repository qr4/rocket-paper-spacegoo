import {
    Appear,
    Col,
    Heading,
    Link,
    Loading,
    Project,
    Row,
    Table,
    Words,
    withStyles,
} from '@arwes/arwes';
import {useParams, useHistory} from 'react-router-dom';
import React, {memo, useRef, useState, useEffect, useCallback} from 'react';

import {BASE_URL} from './Game';
import {PageWrapper} from './components/PageWrapper';
import {SoundWords} from './components';
import {useInterval} from './hooks/useInterval';

const styles = theme => ({
    versusColumnEntry: {
        display: 'flex',
        justifyContent: 'space-evenly',
    },
    summary: {
        marginTop: theme.margin,
        marginBottom: theme.margin * 2,
    },
    rankLoading: {
        padding: [0, theme.padding / 2],
    },
});

const PlayerScoreboard = memo(({show, playerData, classes}) => {
    const history = useHistory();
    const [displayedTableItems, setDisplayedTableItems] = useState(0);
    const refDisplayedTableItems = useRef(0);
    useInterval(() => {
        if (
            playerData &&
            playerData.last_games &&
            refDisplayedTableItems.current < playerData.last_games.length
        ) {
            setDisplayedTableItems(refDisplayedTableItems.current + 1);
            refDisplayedTableItems.current = refDisplayedTableItems.current + 1;
        }
    }, show ? 100 : null);

    return (
        <>
            <Heading node={'h3'}>
                {`${playerData.username}'s scoreboard`}
            </Heading>
            <Table
                animate
                headers={[]}
                dataset={playerData.highscores.map((entry, index) => [
                    index,

                    <Link onClick={() => history.push(`/player/${entry[0]}`)}>
                        <Words
                            animate
                            show={show && displayedTableItems > index}>
                            {entry[0]}
                        </Words>
                    </Link>,

                    entry[1],
                ])}
            />
        </>
    );
});

const PlayerRecentGames = memo(({show, playerData, classes}) => {
    const [displayedTableItems, setDisplayedTableItems] = useState(0);
    const refDisplayedTableItems = useRef(0);
    useInterval(() => {
        if (
            playerData &&
            playerData.last_games &&
            refDisplayedTableItems.current < playerData.last_games.length
        ) {
            setDisplayedTableItems(refDisplayedTableItems.current + 1);
            refDisplayedTableItems.current = refDisplayedTableItems.current + 1;
        }
    }, show ? 100 : null);

    return (
        <>
            <Heading node={'h3'}>
                {`${playerData.username}'s recent games`}
            </Heading>
            <Table
                animate
                dataset={playerData.last_games.map((entry, index) => [
                    entry.game_id,
                    show && (
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
                                    show={show && displayedTableItems > index}>
                                    vs
                                </SoundWords>
                            </sub>{' '}
                            <SoundWords
                                layer="alert"
                                animate
                                show={show && displayedTableItems > index}>
                                {entry.player2}
                            </SoundWords>
                        </div>
                    ),
                    entry.elodiff,
                ])}
            />
        </>
    );
});

export const PlayerPage = withStyles(styles)(({show, classes}) => {
    const {playerName} = useParams();

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

    const [playerData, setPlayerData] = useState(null);
    const loadData = useCallback(
        async () => {
            const data = await fetch(
                `${BASE_URL}/player/${playerName}/info.json`,
            );
            const json = await data.json();
            setPlayerData(json);
        },
        [playerName],
    );
    useInterval(loadData, playerData && playerData.finished ? null : 5000);
    useEffect(loadData, []);

    useInterval(() => {
        if (
            playerData &&
            playerData.last_games &&
            refDisplayedTableItems.current < playerData.last_games.length
        ) {
            setDisplayedTableItems(refDisplayedTableItems.current + 1);
            refDisplayedTableItems.current = refDisplayedTableItems.current + 1;
        }
    }, show ? 100 : null);

    return (
        <PageWrapper>
            <Project show={show} animate header={playerName}>
                {playerData
                    ? anim => (
                          <>
                              <div className={classes.summary}>
                                  <SoundWords animate show={show}>
                                      {`Total of ${
                                          playerData.num_games
                                      } played.`}
                                  </SoundWords>{' '}
                                  <SoundWords animate show={anim.entered}>
                                      Ranked
                                  </SoundWords>{' '}
                                  {showContent ? (
                                      <SoundWords
                                          animate
                                          show={showContent}
                                          layer={
                                              playerData.rank <= 3
                                                  ? 'success'
                                                  : null
                                          }>
                                          {`#${
                                              playerData.rank
                                                  ? playerData.rank.toString()
                                                  : ''
                                          }.`}
                                      </SoundWords>
                                  ) : (
                                      show && (
                                          <span className={classes.rankLoading}>
                                              <Loading animate small />
                                          </span>
                                      )
                                  )}{' '}
                                  <SoundWords animate show={anim.entered}>
                                      View
                                  </SoundWords>{' '}
                                  <Link
                                      onClick={() =>
                                          history.push(
                                              `/player/${
                                                  playerData.username
                                              }/live`,
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
                                      <PlayerScoreboard
                                          show={showContent}
                                          classes={classes}
                                          playerData={playerData}
                                      />
                                  </Col>
                                  <Col s={12} m={12} l={6}>
                                      <PlayerRecentGames
                                          show={showContent}
                                          classes={classes}
                                          playerData={playerData}
                                      />
                                  </Col>
                              </Row>
                          </>
                      )
                    : show && <Loading />}
            </Project>
        </PageWrapper>
    );
});
