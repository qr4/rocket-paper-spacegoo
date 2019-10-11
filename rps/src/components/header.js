import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {Header, Heading, Link, Logo, withStyles} from '@arwes/arwes';
import {faRocket} from '@fortawesome/free-solid-svg-icons';
import React from 'react';

import {Container} from './container';
import {SoundWords} from './';

const styles = themes => ({
    container: {
        display: 'flex',
    },
    logo: {margin: '0.5rem 1rem 0.5rem 0'},
    headingText: {
        marginBottom: 0,
        flexGrow: 1,
        '@global': {
            span: {
                paddingTop: 5,
            },
        },
    },
    linkContainer: {
        display: 'flex',
        alignItems: 'center',
    },
    link: {
        marginLeft: themes.margin,
    },
    linkIcon: {
        marginRight: themes.margin / 2,
    },
});

export const NavBar = withStyles(styles)(({classes}) => {
    return (
        <Header animate>
            <Container className={classes.container}>
                <Heading node="h1" className={classes.headingText}>
                    <Logo className={classes.logo} animate size={50} />
                    <SoundWords animate style={{marginLeft: '5px'}}>
                        Rock Paper Scissors
                    </SoundWords>
                </Heading>
                <div className={classes.linkContainer}>
                    <Link className={classes.link} animate>
                        <FontAwesomeIcon
                            className={classes.linkIcon}
                            icon={faRocket}
                        />
                        Test
                    </Link>
                </div>
            </Container>
        </Header>
    );
});
