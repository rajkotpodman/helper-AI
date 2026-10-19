import React from 'react';
import { 
  Dna, 
  Zap, 
  TrendingUp, 
  ShieldAlert, 
  Play, 
  ArrowRight, 
  Sparkles, 
  Activity, 
  ExternalLink,
  Flame,
  Droplet
} from 'lucide-react';
import { Language, NavigationSection, AudioTrack } from '../../types';
import { HeroMetrics } from './HeroMetrics';
import { INCIDENTS_DATA, AUDIO_TRACKS, TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface ExecutiveOverviewProps {
  lang: Language;
  onNavigate: (section: NavigationSection) => void;
  onPlayTrack: (track: AudioTrack) => void;
}

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({
  lang,
  onNavigate,
  onPlayTrack
}) => {
  const t = TRANSLATIONS[lang];

  return (
    <div className="space-y-6">
      
      {/* Top Hero Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 relative overflow-hidden border-cyan-500/25">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-gradient-to-br from-cyan-500/15 via-teal-500/10 to-transparent rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-rose-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-xs font-mono">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>2026 FRONTIER INTELLIGENCE PARADIGM SHIFT</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            {lang === 'gu'
              ? 'સિલિકોનની 5GW ઉષ્માથી 20W માનવ બાયોલોજીકલ વેટવેર તરફ'
              : 'The Biological Computing Transition & Superintelligence Frontier'}
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
            {lang === 'gu'
              ? 'પરંપરાગત સિલિકોન ચિપ્સ ગ્રહના પાવર ગ્રીડ સાથે અથડાઈ રહી છે. કોર્ટિકલ લેબ્સ CL-1 માનવ ચેતાકોષો, 25 કરોડ ગણી ઉર્જા કાર્યક્ષમતા અને રિકર્સિવ એલાઈનમેન્ટનું વિહંગાવલોકન.'
              : 'As frontier silicon models hit the insurmountable 5GW thermal wall, biological wetware (CL-1 human neuron chips) proves that 20 Watts is sufficient for planetary-scale intelligence. Explore the live transition.'}
          </p>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => {
                audioSynth.playNeuronSpike(700);
                onNavigate('wetware');
              }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono shadow-glow-cyan transition-all hover:scale-105 active:scale-95"
            >
              <Dna size={16} />
              <span>Launch Wetware Lab</span>
            </button>

            <button
              onClick={() => {
                audioSynth.playChirp(650);
                onNavigate('thermodynamics');
              }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-amber-500/30 hover:border-amber-400 text-amber-300 font-bold text-xs font-mono transition-all"
            >
              <Zap size={16} />
              <span>20W vs 5GW Calculator</span>
            </button>

            <button
              onClick={() => {
                audioSynth.playChirp(800);
                onPlayTrack(AUDIO_TRACKS[0]);
              }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-sky-500/30 text-sky-300 text-xs font-mono transition-all"
            >
              <Play size={14} className="fill-sky-300" />
              <span>Listen to Episode 42</span>
            </button>
          </div>
        </div>
      </div>

      {/* Module A: 4 Hero Metric Cards */}
      <HeroMetrics lang={lang} onNavigateSection={onNavigate} />

      {/* Dual Highlights: Wetware Status & Incident Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Highlight: Wetware CL-1 Status (7 cols) */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border-cyan-500/20 space-y-5">
          <div className="flex items-center justify-between border-b border-cyan-500/15 pb-3">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                <Dna size={16} />
              </span>
              <h3 className="text-sm font-bold font-mono uppercase text-slate-200">
                Living In-Vitro Tissue Telemetry (DishBrain CL-1)
              </h3>
            </div>
            <button
              onClick={() => onNavigate('wetware')}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
            >
              Interactive Canvas <ArrowRight size={13} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-cyan-500/15">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Tissue Culture</span>
              <div className="text-lg font-bold font-mono text-white mt-1">804,219 Cells</div>
              <span className="text-[10px] font-mono text-emerald-400">Stem-Cell Derived Cortical</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-cyan-500/15">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Thermal State</span>
              <div className="text-lg font-bold font-mono text-amber-300 mt-1">37.0°C</div>
              <span className="text-[10px] font-mono text-slate-400">Homeostatic Incubator</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-cyan-500/15">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Energy Drawn</span>
              <div className="text-lg font-bold font-mono text-emerald-400 mt-1">20.4 Watts</div>
              <span className="text-[10px] font-mono text-emerald-300">Lightbulb Equivalent</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-cyan-500/20 text-xs text-slate-300 leading-relaxed font-mono">
            <span className="text-cyan-400 font-bold">Key Discovery: </span>
            In-vitro human neurons on microelectrode arrays self-organize without gradient backpropagation. When fed unpredictable chaotic noise on misses, synaptic plasticity rewires connections in under 5 minutes to restore predictability.
          </div>
        </div>

        {/* Right Highlight: Alignment Risk Radar (5 cols) */}
        <div className="lg:col-span-5 glass-panel glass-panel-alert rounded-2xl p-6 border-rose-500/25 space-y-5">
          <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-400">
                <ShieldAlert size={16} />
              </span>
              <h3 className="text-sm font-bold font-mono uppercase text-rose-200">
                Frontier Alignment Risk Radar
              </h3>
            </div>
            <button
              onClick={() => onNavigate('safety')}
              className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1 transition-colors"
            >
              All Logs <ArrowRight size={13} />
            </button>
          </div>

          <div className="space-y-3">
            {INCIDENTS_DATA.slice(0, 2).map((inc) => (
              <div
                key={inc.id}
                onClick={() => onNavigate('safety')}
                className="p-3.5 rounded-xl bg-slate-900/60 border border-rose-500/20 hover:border-rose-500/40 cursor-pointer transition-all space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    {inc.category}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">{inc.date}</span>
                </div>
                <h4 className="text-xs font-bold text-white line-clamp-1">
                  {lang === 'gu' ? inc.titleGu : inc.title}
                </h4>
                <p className="text-[11px] text-slate-400 line-clamp-2">
                  {lang === 'gu' ? inc.descriptionGu : inc.description}
                </p>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2 border-t border-rose-500/15">
            <span>Red-Team Probes: 14 Active</span>
            <span className="text-rose-400 font-bold">Threat: Moderate</span>
          </div>
        </div>

      </div>

    </div>
  );
};
