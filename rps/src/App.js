import './App.css';

import {
  Arwes,
  ThemeProvider,
  createTheme,
  Header,
  Heading,
  Logo,
} from '@arwes/arwes';
import {Howl} from 'howler';
import {Route, BrowserRouter as Router, Switch} from 'react-router-dom';
import React from 'react';

import {SoundsProvider} from '@arwes/sounds';

import { SoundWords } from './components';

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

function App() {
    return (
        <ThemeProvider theme={createTheme()}>
            <SoundsProvider players={players} audio={audio}>
                <Arwes
                    animate
                    background="/background-large.jpg"
                    pattern="/glow.png">
                    <Router>
                        <Header animate>
                            <Heading node="span">
                                <Logo animate size={50} />
                                <SoundWords animate style={{marginLeft: '5px'}}>
                                    Rock Paper Scissors
                                </SoundWords>
                            </Heading>
                        </Header>
                        <Switch>
                            <Route path="/">
                                <Home />
                            </Route>
                        </Switch>
                    </Router>
                </Arwes>
            </SoundsProvider>
        </ThemeProvider>
    );
}

export default App;
