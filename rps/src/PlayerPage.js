import { Project } from '@arwes/arwes';
import {useParams} from 'react-router-dom';
import React from 'react';

import {PageWrapper} from './components/PageWrapper';
import {SoundWords} from './components';

export const PlayerPage = ({show}) => {
    const {playerName} = useParams();
    return (
        <PageWrapper>
            <Project show={show} animate header={playerName}>
                {anim => (
                    <SoundWords animate show={anim.entered}>
                        Oh dear lord what is going on
                    </SoundWords>
                )}
            </Project>
        </PageWrapper>
    );
};
