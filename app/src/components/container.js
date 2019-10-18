import {withStyles} from '@arwes/arwes';
import React from 'react';
import classnames from 'classnames';

const styles = theme => ({
    root: {
        maxWidth: 1316,
        margin: '0 auto',
    },
});

export const Container = withStyles(styles)(({classes, className, children}) => {
    return <div className={classnames(classes.root, className)}>{children}</div>;
});
