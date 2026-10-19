import React, { useState } from 'react';
import { NavigationSection, Language, AudioTrack } from './types';
import { AUDIO_TRACKS } from './lib/constants';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { ExecutiveOverview } from './components/dashboard/ExecutiveOverview';
import { WetwareLab } from './components/wetware/WetwareLab';
import { ThermodynamicCalculator } from './components/calculators/ThermodynamicCalculator';
import { RecursiveMatrix } from './components/recursive/RecursiveMatrix';
import { IncidentTimeline } from './components/safety/IncidentTimeline';
import { AudioPlayer } from './components/audio/AudioPlayer';
import { AgentBridge } from './components/agent/AgentBridge';
import { SearchModal } from './components/common/SearchModal';
import { Play, Pause, Headphones } from 'lucide-react';
import { audioSynth } from './lib/audioSynth';

export function App() {
  const [currentSection, setCurrentSection] = useState<NavigationSection>('overview');
  const [lang, setLang] = useState<Language>('en');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [searchOpen, setSearchOpen] = useState<boolean>(false);
  
  // Audio state
  const [currentTrack, setCurrentTrack] = useState<AudioTrack>(AUDIO_TRACKS[0]);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);

  const toggleAudio = () => {
    const next = !isPlayingAudio;
    setIsPlayingAudio(next);
    if (next) {
      audioSynth.playChirp(720);
    }
  };

  const handleSelectTrack = (track: AudioTrack) => {
    setCurrentTrack(track);
    setIsPlayingAudio(true);
  };

  return (
    <div className="min-h-screen bg-[#080B11] bg-cyber-mesh text-[#F8FAFC] flex flex-col selection:bg-cyan-500 selection:text-black">
      
      {/* Top Navigation Header */}
      <Header
        lang={lang}
        onLanguageChange={setLang}
        onOpenSearch={() => setSearchOpen(true)}
        currentTrack={currentTrack}
        isPlayingAudio={isPlayingAudio}
        onToggleAudio={toggleAudio}
        mobileMenuOpen={mobileMenuOpen}
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
      />

      {/* Main Layout Area */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        
        {/* Collapsible Sidebar */}
        <Sidebar
          currentSection={currentSection}
          onSelectSection={setCurrentSection}
          collapsed={sidebarCollapsed}
          onToggleCollapsed={() => setSidebarCollapsed(!sidebarCollapsed)}
          lang={lang}
          mobileOpen={mobileMenuOpen}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />

        {/* Main Content Viewport */}
        <main className="flex-1 p-4 lg:p-8 min-w-0 pb-28">
          {currentSection === 'overview' && (
            <ExecutiveOverview
              lang={lang}
              onNavigate={setCurrentSection}
              onPlayTrack={handleSelectTrack}
            />
          )}

          {currentSection === 'wetware' && (
            <WetwareLab lang={lang} />
          )}

          {currentSection === 'thermodynamics' && (
            <ThermodynamicCalculator lang={lang} />
          )}

          {currentSection === 'recursive' && (
            <RecursiveMatrix lang={lang} />
          )}

          {currentSection === 'safety' && (
            <IncidentTimeline lang={lang} />
          )}

          {currentSection === 'audio' && (
            <AudioPlayer
              lang={lang}
              currentTrack={currentTrack}
              onSelectTrack={handleSelectTrack}
              isPlaying={isPlayingAudio}
              onTogglePlay={toggleAudio}
            />
          )}

          {currentSection === 'agent' && (
            <AgentBridge lang={lang} />
          )}
        </main>

      </div>

      {/* Persistent Floating Mini-Bar when listening in other sections */}
      {currentSection !== 'audio' && (
        <div className="fixed bottom-4 right-4 z-40 max-w-sm w-full px-4 animate-fade-in">
          <div className="glass-panel rounded-2xl p-3 border-cyan-500/30 flex items-center justify-between gap-3 shadow-2xl bg-slate-950/90 backdrop-blur-xl">
            <div 
              onClick={() => setCurrentSection('audio')}
              className="flex items-center gap-2.5 min-w-0 cursor-pointer group flex-1"
            >
              <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400 group-hover:scale-105 transition-transform flex-shrink-0">
                <Headphones size={18} />
              </div>
              <div className="min-w-0">
                <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block">
                  {isPlayingAudio ? 'Now Playing' : 'Audio Briefing'}
                </span>
                <p className="text-xs font-bold text-white truncate group-hover:text-cyan-300 transition-colors">
                  {lang === 'gu' ? currentTrack.titleGu : currentTrack.title}
                </p>
              </div>
            </div>

            <button
              onClick={toggleAudio}
              className={`p-2.5 rounded-xl flex-shrink-0 transition-all ${
                isPlayingAudio 
                  ? 'bg-cyan-500 text-slate-950 shadow-glow-cyan' 
                  : 'bg-slate-900 border border-cyan-500/30 text-cyan-400 hover:bg-slate-800'
              }`}
            >
              {isPlayingAudio ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
            </button>
          </div>
        </div>
      )}

      {/* Universal Search Modal (Cmd + K) */}
      <SearchModal
        isOpen={searchOpen}
        onClose={() => setSearchOpen(false)}
        onNavigate={setCurrentSection}
        lang={lang}
      />

    </div>
  );
}

export default App;
