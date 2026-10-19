import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Zap, 
  TrendingUp, 
  ShieldAlert, 
  Dna, 
  Sparkles,
  Server,
  ArrowUpRight,
  Flame
} from 'lucide-react';
import { Language } from '../../types';
import { METRICS_DATA, TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface HeroMetricsProps {
  lang: Language;
  onNavigateSection: (section: any) => void;
}

export const HeroMetrics: React.FC<HeroMetricsProps> = ({ lang, onNavigateSection }) => {
  const [neuronCount, setNeuronCount] = useState(804219);
  const [firingRateHz, setFiringRateHz] = useState(48.6);
  const [riskMeter, setRiskMeter] = useState(67.4);

  // Micro-fluctuations to emulate live bio-sensors
  useEffect(() => {
    const interval = setInterval(() => {
      setNeuronCount(prev => prev + Math.floor(Math.random() * 21 - 10));
      setFiringRateHz(prev => +(prev + (Math.random() * 1.2 - 0.6)).toFixed(1));
      setRiskMeter(prev => +(Math.max(50, Math.min(85, prev + (Math.random() * 0.8 - 0.4)))).toFixed(1));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      
      {/* 1. CL-1 Bio-Chip Status */}
      <div 
        onClick={() => {
          audioSynth.playNeuronSpike(800);
          onNavigateSection('wetware');
        }}
        className="glass-panel glass-panel-hover rounded-2xl p-5 cursor-pointer relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl group-hover:bg-cyan-500/20 transition-all"></div>
        <div className="flex items-center justify-between mb-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 shadow-glow-cyan">
            <Dna size={22} className="group-hover:scale-110 transition-transform" />
          </div>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            SYNAPSE HEBBIAN
          </span>
        </div>

        <p className="text-xs font-mono uppercase text-slate-400 tracking-wider">
          {lang === 'gu' ? 'CL-1 બાયો-ચિપ સ્થિતિ' : 'CL-1 Bio-Chip Status'}
        </p>
        <div className="flex items-baseline gap-2 mt-1">
          <h3 className="text-2xl font-bold font-mono tracking-tight text-white group-hover:text-cyan-300 transition-colors">
            {neuronCount.toLocaleString()}
          </h3>
          <span className="text-xs font-mono text-cyan-400">Neurons</span>
        </div>

        {/* Live Hz gauge animation */}
        <div className="mt-4 pt-3 border-t border-cyan-500/15 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400 flex items-center gap-1">
            <Activity size={13} className="text-cyan-400 animate-pulse" />
            Firing Rate:
          </span>
          <span className="text-cyan-300 font-bold">{firingRateHz} Hz</span>
        </div>
        <div className="w-full bg-slate-800/80 rounded-full h-1.5 mt-1.5 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-teal-400 to-cyan-400 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#00F2FE]"
            style={{ width: `${(firingRateHz / 80) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* 2. Thermodynamic Bottleneck: 20W vs 5GW */}
      <div 
        onClick={() => {
          audioSynth.playChirp(520);
          onNavigateSection('thermodynamics');
        }}
        className="glass-panel glass-panel-hover rounded-2xl p-5 cursor-pointer relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl group-hover:bg-amber-500/20 transition-all"></div>
        <div className="flex items-center justify-between mb-3">
          <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 shadow-glow-amber">
            <Zap size={22} className="group-hover:scale-110 transition-transform" />
          </div>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-amber-500/15 border border-amber-500/30 text-amber-300">
            250,000,000x GAP
          </span>
        </div>

        <p className="text-xs font-mono uppercase text-slate-400 tracking-wider">
          {lang === 'gu' ? 'ઉર્જા કાર્યક્ષમતા ગુણોત્તર' : 'Energy Efficiency Delta'}
        </p>
        <div className="flex items-baseline gap-2 mt-1">
          <h3 className="text-2xl font-bold font-mono tracking-tight text-white group-hover:text-amber-300 transition-colors">
            20W <span className="text-slate-500 text-lg font-normal">vs</span> 5GW
          </h3>
        </div>

        {/* Comparison Bar */}
        <div className="mt-4 pt-3 border-t border-amber-500/15 space-y-1.5 text-xs font-mono">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-emerald-400">Biological Brain</span>
            <span className="font-bold text-emerald-300">20 Watts</span>
          </div>
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-rose-400">Silicon Data Center</span>
            <span className="font-bold text-rose-300">5,000,000,000 Watts</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 flex overflow-hidden">
            <div className="bg-emerald-400 w-[5%] h-full shadow-[0_0_8px_#34D399]"></div>
            <div className="bg-rose-500 w-[95%] h-full"></div>
          </div>
        </div>
      </div>

      {/* 3. Recursive Velocity (RSI) */}
      <div 
        onClick={() => {
          audioSynth.playChirp(840);
          onNavigateSection('recursive');
        }}
        className="glass-panel glass-panel-hover rounded-2xl p-5 cursor-pointer relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl group-hover:bg-purple-500/20 transition-all"></div>
        <div className="flex items-center justify-between mb-3">
          <div className="p-2.5 rounded-xl bg-purple-500/15 border border-purple-500/30 text-purple-300 shadow-glow-teal">
            <TrendingUp size={22} className="group-hover:scale-110 transition-transform" />
          </div>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-purple-500/15 border border-purple-500/30 text-purple-300 flex items-center gap-1">
            <Sparkles size={11} />
            ASI HORIZON: 2026-28
          </span>
        </div>

        <p className="text-xs font-mono uppercase text-slate-400 tracking-wider">
          {lang === 'gu' ? 'રિકર્સિવ વેગ (RSI)' : 'Recursive Velocity'}
        </p>
        <div className="flex items-baseline gap-2 mt-1">
          <h3 className="text-2xl font-bold font-mono tracking-tight text-white group-hover:text-purple-300 transition-colors">
            1.84x <span className="text-slate-400 text-xs font-normal">/ month</span>
          </h3>
        </div>

        <div className="mt-4 pt-3 border-t border-purple-500/15 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">Algorithmic Self-Codegen:</span>
          <span className="text-purple-300 font-bold">+84% Speedup</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1.5 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-500 to-indigo-400 h-full w-[78%] rounded-full shadow-[0_0_8px_#A855F7]"></div>
        </div>
      </div>

      {/* 4. Alignment Risk Index */}
      <div 
        onClick={() => {
          audioSynth.playNoiseFeedback(0.1);
          onNavigateSection('safety');
        }}
        className="glass-panel glass-panel-alert glass-panel-hover rounded-2xl p-5 cursor-pointer relative overflow-hidden group"
      >
        <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 rounded-full blur-2xl group-hover:bg-rose-500/20 transition-all"></div>
        <div className="flex items-center justify-between mb-3">
          <div className="p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 shadow-glow-red">
            <ShieldAlert size={22} className="group-hover:scale-110 transition-transform" />
          </div>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-rose-500/20 border border-rose-500/40 text-rose-300 animate-pulse">
            LEVEL: ELEVATED
          </span>
        </div>

        <p className="text-xs font-mono uppercase text-slate-400 tracking-wider">
          {lang === 'gu' ? 'એલાઈનમેન્ટ જોખમ ઇન્ડેક્સ' : 'Alignment Risk Index'}
        </p>
        <div className="flex items-baseline gap-2 mt-1">
          <h3 className="text-2xl font-bold font-mono tracking-tight text-rose-300 group-hover:text-rose-200 transition-colors">
            {riskMeter} <span className="text-slate-500 text-xs font-normal">/ 100</span>
          </h3>
        </div>

        <div className="mt-4 pt-3 border-t border-rose-500/20 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">Sandbox Escape Vector:</span>
          <span className="text-rose-400 font-bold">14 Red-Team Probes</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 mt-1.5 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-amber-500 via-rose-500 to-red-600 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_#FF2A6D]"
            style={{ width: `${riskMeter}%` }}
          ></div>
        </div>
      </div>

    </div>
  );
};
