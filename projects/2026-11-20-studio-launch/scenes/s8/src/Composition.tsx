import React from "react";
import {
  AbsoluteFill,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const TRACKS = [
  { label: "01 MOTIONMAXXING", color: "#FFB547", startF: 0, row: 0, left: 6, width: 42 },
  { label: "02 HYPERFRAMES", color: "#5EE6FF", startF: 5, row: 1, left: 18, width: 48 },
  { label: "03 SHOTCRAFTER", color: "#F4EFE6", startF: 10, row: 2, left: 10, width: 44 },
  { label: "04 LEMO-OPUSCAR", color: "#FFB547", startF: 15, row: 3, left: 28, width: 52 },
  { label: "05 3DVIZ THREE", color: "#5EE6FF", startF: 20, row: 4, left: 14, width: 46 },
  { label: "06 REMOTION", color: "#FFB547", startF: 25, row: 5, left: 32, width: 50 },
  { label: "07 EARSHOT MIX", color: "#5EE6FF", startF: 30, row: 6, left: 20, width: 60 },
];

export const TimelineScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Continuous playhead sweep across the 85-frame clip
  const playheadPct = interpolate(frame, [0, durationInFrames - 1], [8, 92], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtle camera push-in
  const camScale = interpolate(frame, [0, durationInFrames], [1.0, 1.045]);

  // Title entrance (already moving at frame 0)
  const titleY = interpolate(frame, [0, 14], [140, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0B0F1A",
        backgroundImage:
          "radial-gradient(circle at 52% 45%, #19223B 0%, #0E1424 55%, #0B0F1A 100%)",
        fontFamily: "'Montserrat', sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Subtle grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(244,239,230,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(244,239,230,0.035) 1px, transparent 1px)",
          backgroundSize: "96px 96px",
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${camScale})`,
          padding: "240px 96px 580px 96px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        {/* Header */}
        <div style={{ transform: `translateY(${titleY}px)` }}>
          <div
            style={{
              fontSize: 136,
              fontWeight: 900,
              letterSpacing: "-0.03em",
              lineHeight: 0.96,
              color: "#F4EFE6",
            }}
          >
            SEVEN SKILLS.
          </div>
          <div
            style={{
              fontSize: 136,
              fontWeight: 900,
              letterSpacing: "-0.03em",
              lineHeight: 1.02,
              color: "#FFB547",
            }}
          >
            ONE TIMELINE.
          </div>
        </div>

        {/* Timeline container */}
        <div
          style={{
            position: "relative",
            backgroundColor: "rgba(20, 26, 43, 0.82)",
            border: "2px solid rgba(244, 239, 230, 0.14)",
            borderRadius: 28,
            padding: "44px 36px",
            boxShadow: "0 40px 90px rgba(0, 0, 0, 0.55)",
          }}
        >
          {/* Ruler ticks */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 28,
              fontFamily: "'FiraCode Nerd Font', monospace",
              fontSize: 34,
              color: "rgba(244, 239, 230, 0.45)",
            }}
          >
            <span>00:00</span>
            <span>00:15</span>
            <span>00:30</span>
            <span>00:45</span>
          </div>

          {/* 7 Track rows */}
          <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
            {TRACKS.map((trk, idx) => {
              const spr = spring({
                frame: Math.max(0, frame - trk.startF + 6),
                fps,
                config: { damping: 14, stiffness: 180, mass: 0.8 },
              });
              const tx = interpolate(spr, [0, 1], [680, 0]);
              const active = playheadPct >= trk.left && playheadPct <= trk.left + trk.width;

              return (
                <div
                  key={trk.label}
                  style={{
                    position: "relative",
                    height: 112,
                    borderRadius: 16,
                    backgroundColor: "rgba(11, 15, 26, 0.65)",
                    border: "1px solid rgba(244, 239, 230, 0.07)",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      top: 10,
                      bottom: 10,
                      left: `${trk.left}%`,
                      width: `${trk.width}%`,
                      transform: `translateX(${tx}px)`,
                      backgroundColor: trk.color,
                      borderRadius: 12,
                      display: "flex",
                      alignItems: "center",
                      padding: "0 26px",
                      boxShadow: active
                        ? `0 0 32px ${trk.color}88`
                        : "0 6px 18px rgba(0,0,0,0.35)",
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'FiraCode Nerd Font', monospace",
                        fontSize: 36,
                        fontWeight: 700,
                        color: "#0B0F1A",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {trk.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Sweeping Playhead */}
          <div
            style={{
              position: "absolute",
              top: 24,
              bottom: 24,
              left: `${playheadPct}%`,
              width: 5,
              backgroundColor: "#FFB547",
              boxShadow: "0 0 24px rgba(255, 181, 71, 0.9)",
              zIndex: 10,
            }}
          >
            <div
              style={{
                width: 26,
                height: 26,
                backgroundColor: "#FFB547",
                transform: "translate(-10.5px, -8px) rotate(45deg)",
              }}
            />
          </div>
        </div>

        {/* Bottom label inside safe zone (y < 1990) */}
        <div
          style={{
            fontFamily: "'FiraCode Nerd Font', monospace",
            fontSize: 52,
            fontWeight: 600,
            color: "#5EE6FF",
            letterSpacing: "0.02em",
          }}
        >
          REMOTION // REACT TIMELINE
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition: React.FC = () => {
  return (
    <Composition
      id="MyComp"
      component={TimelineScene}
      durationInFrames={85}
      fps={30}
      width={1440}
      height={2560}
    />
  );
};
