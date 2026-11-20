import React from 'react';
import {Composition} from 'remotion';
import {Scene} from './Scene';
export const Root: React.FC = () => (
  <Composition id="S6" component={Scene} width={1440} height={2560} fps={30} durationInFrames={310} />
);
