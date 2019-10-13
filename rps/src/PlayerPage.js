import { Col, Link, Loading, Project, Row, withStyles } from '@arwes/arwes';
import {useParams, useHistory} from 'react-router-dom';
import React, { useState, useEffect, useCallback } from 'react';

import {BASE_URL} from './Game';
import {PageWrapper} from './components/PageWrapper';
import { PlayerScoreboard } from './components/PlayerScoreboard';
import { RecentGames } from './components/RecentGames';
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
    useEffect(
        () => {
            setPlayerData(null);
            loadData();
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [playerName],
    );

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
                                          title={`${playerName}'s scoreboard`}
                                          show={showContent}
                                          classes={classes}
                                          scoreboardData={playerData.highscores}
                                      />
                                  </Col>
                                  <Col s={12} m={12} l={6}>
                                      <RecentGames
                                        title={`${playerName}'s recent games`}
                                          show={showContent}
                                          classes={classes}
                                          lastGamesData={playerData.last_games}
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
