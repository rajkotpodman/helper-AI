import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  Download, 
  Share2, 
  Headphones, 
  Clock, 
  Sparkles,
  Check,
  Disc
} from 'lucide-react';
import { AudioTrack, Language } from '../../types';
import { AUDIO_TRACKS, TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface AudioPlayerProps {
  lang: Language;
  currentTrack: AudioTrack;
  onSelectTrack: (track: AudioTrack) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  lang,
  currentTrack,
  onSelectTrack,
  isPlaying,
  onTogglePlay
}) => {
  const t = TRANSLATIONS[lang];
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [copiedShare, setCopiedShare] = useState<boolean>(false);

  // Audio timer simulation
  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= currentTrack.duration) {
            return 0;
          }
          // Play subtle synthesized voice carrier tone or spike
          if (Math.random() < 0.2) {
            audioSynth.playNeuronSpike(300 + Math.random() * 200, 0.02);
          }
          return +(prev + playbackSpeed).toFixed(1);
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, currentTrack.duration]);

  // Reset time when track changes
  useEffect(() => {
    setCurrentTime(0);
  }, [currentTrack.id]);

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTime(Number(e.target.value));
  };

  const handleSpeedChange = () => {
    const speeds = [1, 1.25, 1.5, 2];
    const nextIdx = (speeds.indexOf(playbackSpeed) + 1) % speeds.length;
    setPlaybackSpeed(speeds[nextIdx]);
    audioSynth.playChirp(700 + nextIdx * 100);
  };

  const handleShare = () => {
    audioSynth.playChirp(800);
    navigator.clipboard?.writeText(window.location.href);
    setCopiedShare(true);
    setTimeout(() => setCopiedShare(false), 2000);
  };

  const handleDownload = () => {
    audioSynth.playChirp(900);
    // Create text transcript file for download
    const transcriptText = currentTrack.transcript
      .map(t => `[${formatSeconds(t.time)}] ${t.text}`)
      .join('\n\n');
    const blob = new Blob([`${currentTrack.title}\n\n${transcriptText}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentTrack.id}-transcript.txt`;
    a.click();
  };

  // Find active transcript paragraph
  const activeTranscriptIdx = currentTrack.transcript.reduce((acc, item, idx) => {
    if (currentTime >= item.time) return idx;
    return acc;
  }, 0);

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden border-sky-500/25">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-sky-500/15 border border-sky-500/30 text-sky-400">
                <Headphones size={20} />
              </span>
              <h2 className="text-xl font-bold text-white tracking-wide">
                {lang === 'gu' ? 'લેક્ચર અને પોડકાસ્ટ પ્લેયર' : 'Biological Wetware & ASI Audio Lectures'}
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              {lang === 'gu'
                ? 'થર્મોડાયનેમિક દિવાલ, ડિશબ્રેઇન ચેતાકોષો અને સુપરઇન્ટેલિજન્સ પર વિજ્ઞાનીઓના ઓડિયો લેક્ચર્સ સાંભળો અને લાઈવ સિંક ટ્રાન્સક્રિપ્ટ વાંચો.'
                : 'Interactive audio briefings exploring biological computing, thermodynamics, and frontier alignment. Real-time transcript synchronization allows deep study.'}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-cyan-500/30 text-cyan-300 text-xs font-mono hover:border-cyan-400 transition-colors"
            >
              <Download size={13} />
              Export Transcript
            </button>
            <button
              onClick={handleShare}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-cyan-500/30 text-cyan-300 text-xs font-mono hover:border-cyan-400 transition-colors"
            >
              {copiedShare ? <Check size={13} className="text-emerald-400" /> : <Share2 size={13} />}
              {copiedShare ? 'Copied Link' : 'Share'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Track Selection & Audio Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Track Playlist (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-mono uppercase text-slate-400 tracking-wider px-1">
            Lecture Catalog ({AUDIO_TRACKS.length})
          </h3>
          
          {AUDIO_TRACKS.map((track) => {
            const isSelected = track.id === currentTrack.id;
            return (
              <div
                key={track.id}
                onClick={() => {
                  audioSynth.playChirp(700);
                  onSelectTrack(track);
                }}
                className={`glass-panel rounded-2xl p-4 cursor-pointer transition-all border ${
                  isSelected 
                    ? 'border-sky-400/50 bg-slate-900/90 shadow-glow-teal' 
                    : 'border-cyan-500/15 hover:border-cyan-500/30'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                      {formatSeconds(track.duration)}
                    </span>
                    <h4 className="text-xs font-bold text-white mt-1 group-hover:text-sky-300 transition-colors">
                      {lang === 'gu' ? track.titleGu : track.title}
                    </h4>
                    <p className="text-[11px] text-slate-400 line-clamp-2">
                      {track.speaker}
                    </p>
                  </div>

                  {isSelected && isPlaying && (
                    <div className="flex items-end gap-0.5 h-4 flex-shrink-0 mt-1">
                      <span className="w-1 h-3 bg-sky-400 animate-pulse"></span>
                      <span className="w-1 h-5 bg-sky-300 animate-pulse delay-75"></span>
                      <span className="w-1 h-2 bg-sky-400 animate-pulse delay-150"></span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Audio Stage & Synced Transcript (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          
          {/* Active Player Card */}
          <div className="glass-panel rounded-2xl p-6 border-sky-500/25 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <span className="text-[10px] font-mono text-sky-400 uppercase tracking-wider">
                  NOW STREAMING
                </span>
                <h3 className="text-base font-bold text-white">
                  {lang === 'gu' ? currentTrack.titleGu : currentTrack.title}
                </h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  {currentTrack.speaker}
                </p>
              </div>

              {/* Speed toggle */}
              <button
                onClick={handleSpeedChange}
                className="self-start sm:self-center px-3 py-1.5 rounded-xl bg-slate-900 border border-cyan-500/30 text-cyan-300 font-mono text-xs hover:border-cyan-400 transition-colors"
              >
                Speed: {playbackSpeed}x
              </button>
            </div>

            {/* Dynamic Animated Frequency Waveform */}
            <div className="h-16 bg-slate-950/80 rounded-xl border border-cyan-500/15 p-3 flex items-center justify-between gap-1 overflow-hidden">
              {Array.from({ length: 36 }).map((_, i) => {
                const heightPercent = isPlaying 
                  ? Math.sin(i * 0.4 + currentTime * 2) * 35 + 45
                  : 15;
                return (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-sky-500 to-cyan-300 rounded-full transition-all duration-150"
                    style={{
                      height: `${Math.max(8, heightPercent)}%`,
                      opacity: i / 36 <= currentTime / currentTrack.duration ? 1 : 0.25
                    }}
                  />
                );
              })}
            </div>

            {/* Seek bar */}
            <div className="space-y-1.5">
              <input
                type="range"
                min={0}
                max={currentTrack.duration}
                step={0.5}
                value={currentTime}
                onChange={handleSeek}
                className="w-full accent-sky-400 cursor-pointer h-2 bg-slate-800 rounded-lg"
              />
              <div className="flex justify-between text-xs font-mono text-slate-400">
                <span>{formatSeconds(currentTime)}</span>
                <span>{formatSeconds(currentTrack.duration)}</span>
              </div>
            </div>

            {/* Playback Controls Bar */}
            <div className="flex items-center justify-center gap-4 pt-2">
              <button
                onClick={() => {
                  audioSynth.playChirp(600);
                  setCurrentTime(prev => Math.max(0, prev - 15));
                }}
                className="p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-cyan-400 transition-colors"
                title="Rewind 15s"
              >
                <SkipBack size={18} />
              </button>

              <button
                onClick={onTogglePlay}
                className="p-4 rounded-2xl bg-gradient-to-r from-sky-400 to-cyan-400 text-slate-950 font-bold shadow-glow-teal hover:scale-105 active:scale-95 transition-all"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} className="ml-1" />}
              </button>

              <button
                onClick={() => {
                  audioSynth.playChirp(750);
                  setCurrentTime(prev => Math.min(currentTrack.duration, prev + 15));
                }}
                className="p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-cyan-400 transition-colors"
                title="Forward 15s"
              >
                <SkipForward size={18} />
              </button>
            </div>
          </div>

          {/* Real-time Synchronized Transcript Viewer */}
          <div className="glass-panel rounded-2xl p-6 border-cyan-500/20 space-y-4">
            <div className="flex items-center justify-between border-b border-cyan-500/15 pb-2.5">
              <h4 className="text-xs font-mono font-bold uppercase text-slate-200 flex items-center gap-2">
                <Sparkles size={14} className="text-sky-400" />
                {t.syncedTranscript}
              </h4>
              <span className="text-[10px] font-mono text-slate-400">
                Click any paragraph to jump audio
              </span>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
              {currentTrack.transcript.map((item, idx) => {
                const isActive = idx === activeTranscriptIdx;
                return (
                  <div
                    key={idx}
                    onClick={() => {
                      audioSynth.playChirp(700);
                      setCurrentTime(item.time);
                    }}
                    className={`p-3.5 rounded-xl cursor-pointer transition-all border ${
                      isActive
                        ? 'bg-sky-500/15 border-sky-400/50 text-white shadow-glow-teal font-medium'
                        : 'bg-slate-900/40 border-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900/70'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300">
                        {formatSeconds(item.time)}
                      </span>
                      {isActive && (
                        <span className="text-[10px] font-mono text-emerald-400 animate-pulse">
                          ▶ CURRENTLY PLAYING
                        </span>
                      )}
                    </div>
                    <p className="text-xs leading-relaxed">
                      {lang === 'gu' ? item.textGu : item.text}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
