import React from 'react';
import './App.css';
import {Route, BrowserRouter as Router, Switch} from "react-router-dom";
import { Arwes, ThemeProvider, createTheme, Header, Heading, Words, Logo } from '@arwes/arwes';

function Home() {
    return "";
}

function App() {
    return (
        <ThemeProvider theme={createTheme()}>
            <Arwes animate background='/background-large.jpg' pattern='/glow.png'>
                <Router>
                    <Header animate>
                        <Heading node="span">
                            <Logo animate size={50}/>
                            <Words animate style={{ marginLeft: '5px'}}>Rock Paper Scissors</Words>
                        </Heading>
                    </Header>
                    <Switch>
                        <Route path="/">
                            <Home />
                        </Route>
                    </Switch>
                </Router>
            </Arwes>
        </ThemeProvider>
    );
}

export default App;
