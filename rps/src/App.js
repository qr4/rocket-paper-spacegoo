import './App.css';

import {Arwes, ThemeProvider, createTheme} from '@arwes/arwes';
import {Howl} from 'howler';
import {Route, BrowserRouter as Router, Switch} from 'react-router-dom';
import React, {useState, useEffect} from 'react';

import {SoundsProvider} from '@arwes/sounds';

import { NavBar } from './components/nav_bar';
import {PlayerPage} from './PlayerPage';

const players = {
    ask: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/ask.mp3`]}),
    click: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/click.mp3`]}),
    deploy: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/deploy.mp3`]}),
    error: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/error.mp3`]}),
    information: new Howl({
        src: [`${process.env.PUBLIC_URL}/sounds/information.mp3`],
    }),
    typing: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/typing.mp3`]}),
    warning: new Howl({src: [`${process.env.PUBLIC_URL}/sounds/warning.mp3`]}),
};
const audio = {
    mute: false,
};

function Home() {
    return '';
}

const AppWrapper = () => (
    <ThemeProvider theme={createTheme()}>
        <SoundsProvider players={players} audio={audio}>
            <Arwes
                animate
                background="/background-large.jpg"
                pattern="/glow.png">
                {anim => <App wrapperAnimEntered={anim.entered} />}
            </Arwes>
        </SoundsProvider>
    </ThemeProvider>
);

function App({wrapperAnimEntered}) {
    const [showContent, setShowContent] = useState(false);
    // Add a nice delay to between Heading and Content animation
    useEffect(
        () => {
            if (wrapperAnimEntered && !showContent) {
                setTimeout(() => {
                    setShowContent && setShowContent(true);
                }, 250);
            }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [wrapperAnimEntered],
    );

    return (
        <Router>
            <NavBar show={wrapperAnimEntered} />
            <Switch>
                <Route path="/player/:playerName">
                    <PlayerPage show={showContent} />
                </Route>
                <Route path="/">
                    <Home show={showContent} />
                </Route>
            </Switch>
        </Router>
    );
}

export default AppWrapper;
