import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Search, 
  Volume2, 
  VolumeX, 
  Globe, 
  ShieldAlert, 
  Play, 
  Pause,
  Menu,
  X,
  Sparkles
} from 'lucide-react';
import { Language, AudioTrack } from '../../types';
import { TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface HeaderProps {
  lang: Language;
  onLanguageChange: (lang: Language) => void;
  onOpenSearch: () => void;
  currentTrack: AudioTrack;
  isPlayingAudio: boolean;
  onToggleAudio: () => void;
  mobileMenuOpen: boolean;
  onToggleMobileMenu: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  lang,
  onLanguageChange,
  onOpenSearch,
  currentTrack,
  isPlayingAudio,
  onToggleAudio,
  mobileMenuOpen,
  onToggleMobileMenu
}) => {
  const [isMuted, setIsMuted] = useState(false);
  const [clock, setClock] = useState('');
  const t = TRANSLATIONS[lang];

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setClock(now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleMute = () => {
    const next = !isMuted;
    setIsMuted(next);
    audioSynth.setMute(next);
    if (!next) {
      audioSynth.playChirp(700);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-cyan-500/20 bg-[#080B11]/80 backdrop-blur-md px-4 lg:px-8 py-3">
      <div className="flex items-center justify-between gap-4 max-w-7xl mx-auto">
        
        {/* Left: Branding & Status Badge */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 rounded-lg bg-slate-900/60 border border-cyan-500/30 text-cyan-400"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div className="flex items-center gap-2.5">
            <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500/20 via-blue-500/10 to-transparent border border-cyan-400/40 shadow-glow-cyan">
              <span className="text-lg">🧬</span>
              <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm tracking-wider uppercase text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-400">
                  AI 2026: Wetware Hub
                </span>
                <span className="hidden sm:inline-block px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                  CL-1 v2.4
                </span>
              </div>
              <div className="hidden md:flex items-center gap-2 text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  CL-1 MEA LIVE
                </span>
                <span>•</span>
                <span className="text-amber-400 flex items-center gap-1">
                  <ShieldAlert size={11} />
                  THREAT: MODERATE
                </span>
                <span>•</span>
                <span className="text-slate-400">{clock}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Center: Search Trigger (Cmd + K) */}
        <div className="hidden md:flex flex-1 max-w-md mx-4">
          <button
            onClick={onOpenSearch}
            className="w-full flex items-center justify-between px-3.5 py-1.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-cyan-500/20 hover:border-cyan-400/40 text-slate-400 text-xs transition-all shadow-inner group"
          >
            <div className="flex items-center gap-2">
              <Search size={14} className="text-cyan-400 group-hover:text-cyan-300 transition-colors" />
              <span>{t.searchPlaceholder}</span>
            </div>
            <kbd className="hidden sm:inline-flex items-center gap-0.5 px-2 py-0.5 text-[10px] font-mono font-semibold text-slate-400 bg-slate-800/80 border border-slate-700 rounded-md">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>
        </div>

        {/* Right: Quick Audio Widget, Audio Sound Synth Toggle, Language & Search button */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Quick Audio Bar */}
          <div className="hidden xl:flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900/70 border border-cyan-500/20">
            <button
              onClick={onToggleAudio}
              className={`p-1.5 rounded-lg transition-colors ${
                isPlayingAudio ? 'bg-cyan-500 text-slate-950 shadow-glow-cyan' : 'bg-slate-800 text-cyan-400 hover:bg-slate-700'
              }`}
              title={isPlayingAudio ? 'Pause Lecture' : 'Play Lecture'}
            >
              {isPlayingAudio ? <Pause size={13} /> : <Play size={13} className="ml-0.5" />}
            </button>
            <div className="text-left w-36 overflow-hidden">
              <p className="text-[11px] font-medium text-slate-200 truncate">{currentTrack.title}</p>
              <div className="flex items-center gap-1">
                {isPlayingAudio ? (
                  <div className="flex items-end gap-0.5 h-2.5">
                    <span className="w-0.5 h-2 bg-cyan-400 animate-pulse"></span>
                    <span className="w-0.5 h-3 bg-cyan-300 animate-pulse delay-75"></span>
                    <span className="w-0.5 h-1.5 bg-cyan-400 animate-pulse delay-150"></span>
                    <span className="w-0.5 h-2.5 bg-cyan-300 animate-pulse"></span>
                  </div>
                ) : (
                  <span className="text-[10px] font-mono text-slate-400">Audio Ready</span>
                )}
              </div>
            </div>
          </div>

          {/* Sound FX Toggle (Neuron Clicks) */}
          <button
            onClick={toggleMute}
            className={`p-2 rounded-xl border text-xs transition-all ${
              isMuted 
                ? 'bg-slate-900/50 border-slate-700/50 text-slate-500 hover:text-slate-400' 
                : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300 hover:border-cyan-400 shadow-glow-cyan'
            }`}
            title={isMuted ? 'Unmute Neural Action Potentials' : 'Mute Neural Clicks'}
          >
            {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>

          {/* Mobile Search button */}
          <button
            onClick={onOpenSearch}
            className="md:hidden p-2 rounded-xl bg-slate-900/60 border border-cyan-500/30 text-cyan-400"
            aria-label="Search"
          >
            <Search size={16} />
          </button>

          {/* Language Switcher */}
          <div className="flex items-center p-1 rounded-xl bg-slate-900/80 border border-cyan-500/20 text-xs font-mono">
            <button
              onClick={() => {
                audioSynth.playChirp(600);
                onLanguageChange('en');
              }}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                lang === 'en'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-glow-cyan'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => {
                audioSynth.playChirp(750);
                onLanguageChange('gu');
              }}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                lang === 'gu'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-glow-cyan'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="ગુજરાતી ભાષા"
            >
              ગુજ
            </button>
          </div>

        </div>

      </div>
    </header>
  );
};
