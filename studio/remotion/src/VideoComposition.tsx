/**
 * Remotion Video Composition
 * Assembles video clips with transitions, audio, and captions
 */
import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  Video,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from 'remotion';

interface Clip {
  id: string;
  sequence: number;
  startFrame: number;
  durationInFrames: number;
  videoUrl: string;
  audioUrl?: string;
  transition: 'cut' | 'fade' | 'dissolve' | 'wipe';
  captions?: {
    text: string;
    style: string;
    enabled: boolean;
  };
}

interface CompositionData {
  clips: Clip[];
  title: string;
  fps: number;
  width: number;
  height: number;
}

export const VideoComposition: React.FC<{ data: CompositionData }> = ({
  data,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {data.clips.map((clip, index) => (
        <ClipSequence
          key={clip.id}
          clip={clip}
          nextClip={data.clips[index + 1]}
        />
      ))}
    </AbsoluteFill>
  );
};

const ClipSequence: React.FC<{
  clip: Clip;
  nextClip?: Clip;
}> = ({ clip, nextClip }) => {
  return (
    <Sequence
      from={clip.startFrame}
      durationInFrames={clip.durationInFrames}
    >
      <AbsoluteFill>
        {/* Video layer */}
        <VideoLayer clip={clip} nextClip={nextClip} />

        {/* Audio layer */}
        {clip.audioUrl && (
          <Audio src={clip.audioUrl} volume={1} />
        )}

        {/* Caption layer */}
        {clip.captions?.enabled && (
          <CaptionLayer text={clip.captions.text} style={clip.captions.style} />
        )}
      </AbsoluteFill>
    </Sequence>
  );
};

const VideoLayer: React.FC<{
  clip: Clip;
  nextClip?: Clip;
}> = ({ clip, nextClip }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate transition opacity
  const transitionDuration = fps * 0.5; // 0.5 second transition
  const opacity = calculateTransitionOpacity(
    frame,
    clip.durationInFrames,
    transitionDuration,
    clip.transition
  );

  return (
    <AbsoluteFill style={{ opacity }}>
      <Video
        src={clip.videoUrl}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />
    </AbsoluteFill>
  );
};

const CaptionLayer: React.FC<{
  text: string;
  style: string;
}> = ({ text, style }) => {
  const frame = useCurrentFrame();

  // Animate caption entrance
  const opacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const translateY = interpolate(frame, [0, 10], [20, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: style === 'bottom-third' ? 'flex-end' : 'center',
        alignItems: 'center',
        padding: '40px',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          padding: '20px 40px',
          borderRadius: '10px',
          opacity,
          transform: `translateY(${translateY}px)`,
        }}
      >
        <p
          style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#fff',
            textAlign: 'center',
            margin: 0,
            fontFamily: 'Arial, sans-serif',
            lineHeight: 1.4,
          }}
        >
          {text}
        </p>
      </div>
    </AbsoluteFill>
  );
};

function calculateTransitionOpacity(
  frame: number,
  duration: number,
  transitionDuration: number,
  transitionType: string
): number {
  if (transitionType === 'cut') {
    return 1;
  }

  // Fade in at start
  if (frame < transitionDuration) {
    return frame / transitionDuration;
  }

  // Fade out at end
  if (frame > duration - transitionDuration) {
    return (duration - frame) / transitionDuration;
  }

  return 1;
}

// Export composition configuration
export const RemotionComposition = {
  id: 'VideoComposition',
  component: VideoComposition,
  defaultProps: {
    data: {
      clips: [],
      title: 'AI Studio Video',
      fps: 30,
      width: 1920,
      height: 1080,
    },
  },
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
