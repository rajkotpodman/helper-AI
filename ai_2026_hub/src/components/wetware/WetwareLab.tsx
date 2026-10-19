import React, { useState, useEffect, useRef } from 'react';
import { 
  Dna, 
  Zap, 
  Activity, 
  Droplet, 
  Flame, 
  Sparkles, 
  Volume2, 
  VolumeX,
  Play, 
  RefreshCw,
  Sliders,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Language, NeuronNode } from '../../types';
import { TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface WetwareLabProps {
  lang: Language;
}

export const WetwareLab: React.FC<WetwareLabProps> = ({ lang }) => {
  const t = TRANSLATIONS[lang];
  const [neurons, setNeurons] = useState<NeuronNode[]>([]);
  const [selectedNeuron, setSelectedNeuron] = useState<NeuronNode | null>(null);
  const [noiseMode, setNoiseMode] = useState<boolean>(false);
  const [stimulationCount, setStimulationCount] = useState<number>(142);
  const [entropyLevel, setEntropyLevel] = useState<number>(0.28);
  const [isIncubating, setIsIncubating] = useState<boolean>(true);
  const [nutrientPuffActive, setNutrientPuffActive] = useState<boolean>(false);

  // Initialize neural grid (representing ~800k biological neurons on MEA grid)
  useEffect(() => {
    const initialNodes: NeuronNode[] = [];
    const count = 38;
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * 2 * Math.PI;
      const radius = 90 + Math.random() * 110;
      initialNodes.push({
        id: i,
        x: 250 + radius * Math.cos(angle) + (Math.random() * 20 - 10),
        y: 200 + radius * Math.sin(angle) * 0.75 + (Math.random() * 20 - 10),
        firing: false,
        activityLevel: +(Math.random() * 0.8 + 0.2).toFixed(2),
        synapses: [
          (i + 1) % count,
          (i + 3) % count,
          (i + 7) % count
        ],
        membranePotential: -70 + Math.floor(Math.random() * 15)
      });
    }
    setNeurons(initialNodes);
    setSelectedNeuron(initialNodes[0]);
  }, []);

  // Autonomous spontaneous firing loop (emulating real in-vitro cortical tissue)
  useEffect(() => {
    const timer = setInterval(() => {
      setNeurons(prev => {
        return prev.map(n => {
          const willFire = Math.random() < (noiseMode ? 0.35 : 0.12);
          if (willFire) {
            audioSynth.playNeuronSpike(500 + n.id * 15, 0.03);
          }
          return {
            ...n,
            firing: willFire,
            membranePotential: willFire ? 35 : -70 + Math.floor(Math.random() * 12)
          };
        });
      });

      // Fluctuate entropy based on noise mode
      setEntropyLevel(prev => {
        if (noiseMode) {
          return +(Math.min(0.85, prev + 0.04)).toFixed(2);
        } else {
          return +(Math.max(0.18, prev - 0.02)).toFixed(2);
        }
      });
    }, 450);

    return () => clearInterval(timer);
  }, [noiseMode]);

  // Handle manual electrode stimulus (Ping)
  const triggerElectricPing = () => {
    audioSynth.playNeuronSpike(950, 0.08);
    audioSynth.playChirp(820);
    setStimulationCount(c => c + 1);

    // Propagate action potentials across all connected neurons
    setNeurons(prev => {
      return prev.map((n, idx) => ({
        ...n,
        firing: idx % 2 === 0,
        membranePotential: idx % 2 === 0 ? 40 : -55
      }));
    });

    setTimeout(() => {
      setNeurons(prev => prev.map(n => ({ ...n, firing: false, membranePotential: -70 })));
    }, 300);
  };

  // Toggle DishBrain unpredictable noise vs structured reinforcement
  const toggleFeedbackNoise = () => {
    const next = !noiseMode;
    setNoiseMode(next);
    if (next) {
      audioSynth.playNoiseFeedback(0.2);
    } else {
      audioSynth.playChirp(600);
    }
  };

  // Trigger nutrient infusion
  const triggerNutrientPuff = () => {
    audioSynth.playChirp(1050);
    setNutrientPuffActive(true);
    setTimeout(() => setNutrientPuffActive(false), 2000);
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden border-cyan-500/25">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                <Dna size={20} />
              </span>
              <h2 className="text-xl font-bold text-white tracking-wide">
                {lang === 'gu' ? 'જૈવિક વેટવેર (CL-1) લેબ' : 'Biological Wetware (CL-1) Microelectrode Lab'}
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              {lang === 'gu'
                ? 'કોર્ટિકલ લેબ્સ CL-1 ચિપ પર 800,000 જીવંત માનવ ચેતાકોષો સાથે લાઈવ ઇન્ટરેક્શન. ઇલેક્ટ્રિકલ સિગ્નલ આપો અને ફ્રી એનર્જી પ્રિન્સિપલ જુઓ.'
                : 'Interact with living human cortical neurons cultured over high-density CMOS Microelectrode Arrays (MEAs). Observe real-time action potentials, Free Energy Principle self-organization, and synthetic Hebbian plasticity.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-emerald-500/30 text-emerald-300 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              CL-1 INCUBATOR: 37.0°C | pH 7.35
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Canvas / Visualizer (8 cols) */}
        <div className="lg:col-span-8 glass-panel rounded-2xl p-5 flex flex-col justify-between border-cyan-500/20 relative overflow-hidden min-h-[480px]">
          
          {/* Top Canvas Controls & HUD */}
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-cyan-300 px-2.5 py-1 rounded bg-cyan-950/60 border border-cyan-500/30">
                MEA GRID: 4,096 Electrodes
              </span>
              <span className={`text-xs font-mono px-2.5 py-1 rounded border transition-colors ${
                noiseMode 
                  ? 'bg-rose-950/60 text-rose-300 border-rose-500/40' 
                  : 'bg-emerald-950/60 text-emerald-300 border-emerald-500/40'
              }`}>
                FEEDBACK: {noiseMode ? 'UNPREDICTABLE NOISE' : 'STRUCTURED FREQUENCY'}
              </span>
            </div>

            <div className="text-right">
              <span className="text-[11px] font-mono text-slate-400">Tissue Free Energy:</span>
              <div className="text-xs font-bold font-mono text-cyan-400">
                Entropy: {entropyLevel} ({entropyLevel < 0.35 ? 'Stabilized' : 'Chaotic'})
              </div>
            </div>
          </div>

          {/* SVG Neural Network & Synapses */}
          <div className="relative my-4 flex-1 flex items-center justify-center">
            <svg 
              className="w-full h-80 max-w-xl" 
              viewBox="0 0 500 400"
            >
              <defs>
                {/* Glow Filter */}
                <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
                <radialGradient id="chipCenter" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#00F2FE" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#080B11" stopOpacity="0" />
                </radialGradient>
              </defs>

              {/* Silicon CMOS Array Matrix Underlay */}
              <circle cx="250" cy="200" r="160" fill="url(#chipCenter)" stroke="rgba(0,242,254,0.12)" strokeDasharray="3 3" />
              <circle cx="250" cy="200" r="100" fill="none" stroke="rgba(79,172,254,0.08)" />

              {/* MEA Microgrid points */}
              {Array.from({ length: 9 }).map((_, r) =>
                Array.from({ length: 11 }).map((_, c) => (
                  <circle
                    key={`${r}-${c}`}
                    cx={130 + c * 24}
                    cy={100 + r * 25}
                    r="1"
                    fill="rgba(0,242,254,0.18)"
                  />
                ))
              )}

              {/* Synaptic Axon Connections */}
              {neurons.map((node) =>
                node.synapses.map((targetId) => {
                  const target = neurons[targetId];
                  if (!target) return null;
                  const isSynapseFiring = node.firing || target.firing;
                  return (
                    <line
                      key={`${node.id}-${targetId}`}
                      x1={node.x}
                      y1={node.y}
                      x2={target.x}
                      y2={target.y}
                      stroke={isSynapseFiring ? '#00F2FE' : 'rgba(79, 172, 254, 0.22)'}
                      strokeWidth={isSynapseFiring ? 2 : 0.8}
                      filter={isSynapseFiring ? 'url(#neonGlow)' : undefined}
                      strokeDasharray={isSynapseFiring ? '6 2' : undefined}
                      className={isSynapseFiring ? 'animate-pulse' : ''}
                    />
                  );
                })
              )}

              {/* Living Human Neurons (Soma) */}
              {neurons.map((n) => {
                const isSelected = selectedNeuron?.id === n.id;
                return (
                  <g 
                    key={n.id} 
                    onClick={() => {
                      audioSynth.playNeuronSpike(600 + n.id * 10, 0.05);
                      setSelectedNeuron(n);
                    }}
                    className="cursor-pointer group"
                  >
                    {/* Outer Firing Halo */}
                    {n.firing && (
                      <circle
                        cx={n.x}
                        cy={n.y}
                        r="14"
                        fill="rgba(0, 242, 254, 0.35)"
                        filter="url(#neonGlow)"
                        className="animate-ping"
                      />
                    )}

                    {/* Neuron Soma Cell Body */}
                    <circle
                      cx={n.x}
                      cy={n.y}
                      r={isSelected ? 7 : (n.firing ? 5.5 : 4)}
                      fill={n.firing ? '#00F2FE' : (isSelected ? '#FFB300' : '#4FACFE')}
                      stroke={isSelected ? '#FFFFFF' : '#080B11'}
                      strokeWidth={1.5}
                      filter="url(#neonGlow)"
                    />
                  </g>
                );
              })}

              {/* Electrode Stimulus Ping Wave Effect */}
              {nutrientPuffActive && (
                <circle
                  cx="250"
                  cy="200"
                  r="180"
                  fill="none"
                  stroke="#34D399"
                  strokeWidth="3"
                  className="animate-ping"
                  opacity="0.6"
                />
              )}
            </svg>
          </div>

          {/* Bottom Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-cyan-500/15 z-10">
            <div className="flex flex-wrap items-center gap-2">
              {/* Electric Ping Button */}
              <button
                onClick={triggerElectricPing}
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-glow-cyan transition-all active:scale-95"
              >
                <Zap size={14} />
                {t.pingNeuron}
              </button>

              {/* DishBrain Noise Toggle */}
              <button
                onClick={toggleFeedbackNoise}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-mono border transition-all ${
                  noiseMode
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500 shadow-glow-red'
                    : 'bg-slate-900/80 text-cyan-300 border-cyan-500/30 hover:border-cyan-400'
                }`}
              >
                <Activity size={14} />
                {noiseMode ? 'Punish: Unpredictable Noise' : 'Reward: Sine Wave'}
              </button>

              {/* Nutrient Infusion */}
              <button
                onClick={triggerNutrientPuff}
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 text-xs font-mono transition-all"
              >
                <Droplet size={14} />
                {t.triggerPuff}
              </button>
            </div>

            <div className="text-[11px] font-mono text-slate-400">
              Total Electrical Probes: <span className="text-white font-bold">{stimulationCount}</span>
            </div>
          </div>
        </div>

        {/* Telemetry & Neuron Inspector (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* Selected Neuron Inspector Card */}
          <div className="glass-panel rounded-2xl p-5 border-cyan-500/20 space-y-4">
            <div className="flex items-center justify-between border-b border-cyan-500/15 pb-2.5">
              <h3 className="text-xs font-mono font-bold uppercase text-slate-200 flex items-center gap-2">
                <Sparkles size={14} className="text-amber-400" />
                Neuron Soma Inspector
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Cell #{selectedNeuron ? selectedNeuron.id : 0}
              </span>
            </div>

            {selectedNeuron ? (
              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Membrane Potential:</span>
                  <span className={`font-bold ${
                    selectedNeuron.membranePotential > -50 ? 'text-amber-300' : 'text-cyan-300'
                  }`}>
                    {selectedNeuron.membranePotential} mV
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Synaptic Dendrites:</span>
                  <span className="text-white font-bold">
                    {selectedNeuron.synapses.length} Connections
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Plasticity (Hebbian):</span>
                  <span className="text-emerald-400 font-bold">
                    {(selectedNeuron.activityLevel * 100).toFixed(0)}% Reinforced
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Action Potential:</span>
                  <span className={`font-bold ${
                    selectedNeuron.firing ? 'text-cyan-400 animate-pulse' : 'text-slate-400'
                  }`}>
                    {selectedNeuron.firing ? 'ACTIVE DEPOLARIZATION' : 'RESTING STATE'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-cyan-500/15 text-[11px] text-slate-300 leading-relaxed">
                  Cortical neurons obey Karl Fristons Free Energy Principle: By applying electrical stimuli upon incorrect decisions, the cellular array rewires its synapses to maintain homeostatic predictability.
                </div>
              </div>
            ) : null}
          </div>

          {/* Biological Incubator Telemetry */}
          <div className="glass-panel rounded-2xl p-5 border-cyan-500/20 space-y-3 font-mono text-xs">
            <h4 className="text-xs font-bold uppercase text-slate-200 border-b border-cyan-500/15 pb-2 flex items-center gap-2">
              <Activity size={14} className="text-emerald-400" />
              Incubation Chamber Life Support
            </h4>

            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Flame size={12} className="text-amber-400" />
                Temperature:
              </span>
              <span className="text-emerald-300 font-bold">37.0°C ± 0.1</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Droplet size={12} className="text-sky-400" />
                pH Sensor:
              </span>
              <span className="text-cyan-300 font-bold">7.35 (Homeostatic)</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Activity size={12} className="text-purple-400" />
                Glucose Perfusion:
              </span>
              <span className="text-purple-300 font-bold">0.42 mL / hr</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400 flex items-center gap-1.5">
                <CheckCircle2 size={12} className="text-emerald-400" />
                Electrode Impedance:
              </span>
              <span className="text-emerald-300 font-bold">12.4 kΩ (Optimal)</span>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
