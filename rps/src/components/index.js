import { Button, Words } from '@arwes/arwes';
import React from 'react';

import {withSounds} from '@arwes/sounds';

const withCoolSounds = () => InnerComp =>
    withSounds()(props => <InnerComp {...props} sounds={props.players} />);

export const SoundButton = withCoolSounds()(Button);
export const SoundWords = withCoolSounds()(Words);

// Links don't do sound
// export const SoundLink = withCoolSounds()(Link);
