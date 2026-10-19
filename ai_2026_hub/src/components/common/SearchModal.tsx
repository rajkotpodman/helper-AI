import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  X, 
  ArrowRight, 
  Dna, 
  Zap, 
  ShieldAlert, 
  Headphones, 
  Bot, 
  Sparkles,
  Layers
} from 'lucide-react';
import { NavigationSection, Language } from '../../types';
import { INCIDENTS_DATA, AUDIO_TRACKS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (section: NavigationSection) => void;
  lang: Language;
}

export const SearchModal: React.FC<SearchModalProps> = ({
  isOpen,
  onClose,
  onNavigate,
  lang
}) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
    }
  }, [isOpen]);

  // Global key shortcut Cmd+K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          audioSynth.playChirp(750);
          // Handled in parent
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Search items index
  const searchIndex = [
    {
      title: 'Biological Wetware (CL-1) Lab',
      desc: 'Interactive 800k living human neurons cultured on Microelectrode Arrays',
      section: 'wetware' as NavigationSection,
      icon: Dna,
      category: 'Lab Module'
    },
    {
      title: 'Thermodynamic Bottleneck Calculator',
      desc: 'Compare 20W biological brain against 5GW Silicon data center cooling needs',
      section: 'thermodynamics' as NavigationSection,
      icon: Zap,
      category: 'Calculator'
    },
    {
      title: 'Recursive Self-Improvement & ASI Matrix',
      desc: 'Exponential self-compilation curves and algorithmic acceleration timeline',
      section: 'recursive' as NavigationSection,
      icon: Sparkles,
      category: 'Singularity'
    },
    {
      title: 'AI Safety & Alignment Incident Logs',
      desc: 'Telemetry from Anthropic control test, Apollo research, and cyber breaches',
      section: 'safety' as NavigationSection,
      icon: ShieldAlert,
      category: 'Safety'
    },
    {
      title: 'Audio Lectures & Podcasts',
      desc: 'The 20W Miracle, DishBrain to CL-1, and Singularity threshold episodes',
      section: 'audio' as NavigationSection,
      icon: Headphones,
      category: 'Audio'
    },
    {
      title: 'Helper-AI Autonomous Agent Bridge',
      desc: 'Direct neural link with Helper-AI background Python agent engine',
      section: 'agent' as NavigationSection,
      icon: Bot,
      category: 'Agent'
    },
    // Incidents index
    ...INCIDENTS_DATA.map(inc => ({
      title: inc.title,
      desc: inc.description,
      section: 'safety' as NavigationSection,
      icon: ShieldAlert,
      category: 'Incident'
    })),
    // Audio lectures index
    ...AUDIO_TRACKS.map(track => ({
      title: track.title,
      desc: track.summary,
      section: 'audio' as NavigationSection,
      icon: Headphones,
      category: 'Podcast'
    }))
  ];

  const results = searchIndex.filter(item => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return item.title.toLowerCase().includes(q) || item.desc.toLowerCase().includes(q) || item.category.toLowerCase().includes(q);
  }).slice(0, 7);

  const handleSelect = (section: NavigationSection) => {
    audioSynth.playChirp(700);
    onNavigate(section);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-2xl rounded-2xl bg-[#0B0F19] border border-cyan-500/30 shadow-2xl overflow-hidden shadow-glow-cyan"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-cyan-500/20 bg-slate-900/50">
          <Search size={18} className="text-cyan-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search wetware papers, 20W thermodynamic limits, incident logs..."
            className="w-full bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none font-mono"
          />
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Results List */}
        <div className="p-3 max-h-96 overflow-y-auto space-y-1">
          {results.length > 0 ? (
            results.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  onClick={() => handleSelect(item.section)}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-cyan-500/10 hover:border-cyan-500/30 border border-transparent cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-slate-900 border border-cyan-500/20 text-cyan-400 group-hover:text-cyan-300">
                      <Icon size={16} />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors truncate">
                          {item.title}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate max-w-lg mt-0.5">
                        {item.desc}
                      </p>
                    </div>
                  </div>

                  <ArrowRight size={14} className="text-slate-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all flex-shrink-0 ml-2" />
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs font-mono text-slate-400">
              No matching intelligence documents found for "{query}".
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-5 py-2.5 bg-slate-950 border-t border-cyan-500/15 flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span>Navigate with mouse or arrow keys</span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
};
