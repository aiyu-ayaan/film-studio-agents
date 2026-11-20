import React from 'react';
import {AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame} from 'remotion';

const INK = '#0E1220', MIST = '#7C8DA8', PAPER = '#EDE6D6', EMBER = '#F2A33A';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const font = new FontFace('Cormorant Garamond', `url(${staticFile('cormorant-garamond-latin-700-normal.woff2')})`, {weight: '700'});
document.fonts.add(font);
font.load();

const Hand: React.FC<{open: number; mirror?: boolean}> = ({open, mirror}) => {
  const fingers = [0, 1, 2, 3].map((i) => {
    const ang = interpolate(open, [0, 1], [8 - i * 3, -78 - i * 4]);
    return (
      <rect key={i} x={0} y={-37} width={215 - Math.abs(i - 1.5) * 18} height={74} rx={37}
        fill={i % 2 ? '#2A3550' : '#34405E'} stroke="#0A0E1A" strokeWidth={4}
        transform={`translate(-150 ${-105 + i * 78}) rotate(${ang})`} />
    );
  });
  const thumb = (
    <rect x={0} y={-40} width={190} height={80} rx={40} fill="#34405E" stroke="#0A0E1A" strokeWidth={4}
      transform={`translate(-230 -150) rotate(${interpolate(open, [0, 1], [-35, -105])})`} />
  );
  return (
    <g transform={mirror ? 'scale(-1 1)' : undefined}>
      <rect x={-440} y={-150} width={310} height={330} rx={100} fill="#2A3550" stroke="#0A0E1A" strokeWidth={4} />
      {thumb}
      {fingers}
    </g>
  );
};

export const Scene: React.FC = () => {
  const f = useCurrentFrame();
  const open = Easing.inOut(Easing.cubic)(interpolate(f, [150, 195], [0, 1], clamp));
  const tension = interpolate(f, [0, 140], [0.15, 1], clamp) * (f < 150 ? 1 : interpolate(f, [150, 162], [1, 0], clamp));
  const sx = (Math.sin(f * 2.9) + Math.sin(f * 5.3 + 1)) * 7 * tension;
  const sy = (Math.sin(f * 3.7 + 2) + Math.sin(f * 6.1)) * 6 * tension;
  // clenched hands squeeze together, then part
  const gap = interpolate(open, [0, 1], [-10 + Math.sin(f * 0.5) * 3 * tension, 150]);
  // ember
  const lift = Easing.in(Easing.cubic)(interpolate(f, [190, 262], [0, 1], clamp));
  const pulse = 1 + Math.sin(f * 0.35) * 0.06 * (1 - open);
  const emberY = -lift * 1000 - open * 70;
  const emberOp = interpolate(f, [235, 275], [1, 0], clamp);
  const emberScale = pulse * interpolate(lift, [0, 1], [1, 0.45]) * interpolate(open, [0, 1], [0.8, 1.15]);
  const textIn = interpolate(f, [215, 255], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const handY = open * 40;
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, #1A2038 0%, ${INK} 70%)`, overflow: 'hidden'}}>
      <svg width={1440} height={2560} viewBox="0 0 1440 2560" style={{position: 'absolute'}}>
        <defs>
          <radialGradient id="glow">
            <stop offset="0" stopColor="#FFE9B8" stopOpacity="1" />
            <stop offset="0.25" stopColor={EMBER} stopOpacity="0.9" />
            <stop offset="1" stopColor={EMBER} stopOpacity="0" />
          </radialGradient>
          <radialGradient id="vig" cx="50%" cy="50%" r="75%">
            <stop offset="0.55" stopColor="#000" stopOpacity="0" />
            <stop offset="1" stopColor="#000" stopOpacity="0.55" />
          </radialGradient>
          <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" /><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.9 0" /></filter>
        </defs>
        <g transform={`translate(${720 + sx} ${1050 + sy}) scale(1.1)`}>
          <g transform={`translate(0 ${emberY}) scale(${emberScale})`} opacity={emberOp}>
            <circle r={330} fill="url(#glow)" opacity={0.55 + open * 0.3} />
            <circle r={85} fill="url(#glow)" />
            <circle r={34} fill="#FFF3D6" />
          </g>
          <g transform={`translate(${-gap} ${handY})`}><Hand open={open} /></g>
          <g transform={`translate(${gap} ${handY})`}><Hand open={open} mirror /></g>
          <circle r={260} fill="url(#glow)" opacity={(1 - open) * (0.35 + 0.15 * Math.sin(f * 0.35))} style={{mixBlendMode: 'screen'}} />
        </g>
        <rect width={1440} height={2560} fill="url(#vig)" />
        <rect width={1440} height={2560} filter="url(#grain)" opacity={0.03} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 1640, textAlign: 'center', fontFamily: "'Cormorant Garamond', serif", fontWeight: 700, fontSize: 190, letterSpacing: 8, color: EMBER, opacity: textIn, transform: `translateY(${(1 - textIn) * 30}px)`, textShadow: `0 0 50px rgba(242,163,58,.45)`}}>
        LET IT GO.
      </div>
    </AbsoluteFill>
  );
};
