import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {
    Header,
    Heading,
    Link as ArwesLink,
    Logo,
    withStyles,
} from '@arwes/arwes';
import {useHistory} from 'react-router-dom';
import {faRocket, faSatellite} from '@fortawesome/free-solid-svg-icons';
import React from 'react';

import {Container} from './container';
import {SoundWords} from './';

const styles = themes => ({
    root: {
    },
    container: {
        display: 'flex',
        marginBottom: '2rem',
    },
    logo: {margin: '0.5rem 1rem 0.5rem 0'},
    headingText: {
        marginBottom: 0,
        flexGrow: 1,
        '@global': {
            span: {
                paddingTop: 3,
            },
        },
    },
    linkContainer: {
        display: 'flex',
        alignItems: 'center',
    },
    link: {
        margin: [0, themes.margin],
    },
    linkIcon: {
        marginRight: themes.margin / 2,
    },
});

export const NavBar = withStyles(styles)(({show, classes}) => {
    const history = useHistory();
    return (
        <Header animate className={classes.root}>
            <Container className={classes.container}>
                <Heading node="span" className={classes.headingText}>
                    <Logo className={classes.logo} animate size={50} />
                    <SoundWords animate style={{marginLeft: '5px'}} show={show}>
                        Rock Paper Scissors
                    </SoundWords>
                </Heading>
                <div className={classes.linkContainer}>
                    <ArwesLink
                        className={classes.link}
                        animate
                        href="https://github.com/qr4/rocket-paper-spacegoo">
                        <FontAwesomeIcon
                            className={classes.linkIcon}
                            icon={faSatellite}
                        />
                        SourceCode
                    </ArwesLink>
                    <ArwesLink
                        className={classes.link}
                        href="#"
                        onClick={() => history.push('/')}>
                        <FontAwesomeIcon
                            className={classes.linkIcon}
                            icon={faRocket}
                        />
                        Home
                    </ArwesLink>
                </div>
            </Container>
        </Header>
    );
});
