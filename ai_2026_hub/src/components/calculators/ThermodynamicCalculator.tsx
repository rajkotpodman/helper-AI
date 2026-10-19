import React, { useState, useMemo } from 'react';
import { 
  Zap, 
  Droplet, 
  Flame, 
  Leaf, 
  Dna, 
  Gauge, 
  Sliders, 
  Activity, 
  AlertTriangle,
  Factory,
  Layers,
  ArrowRight
} from 'lucide-react';
import { Language } from '../../types';
import { TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface ThermodynamicCalculatorProps {
  lang: Language;
}

export const ThermodynamicCalculator: React.FC<ThermodynamicCalculatorProps> = ({ lang }) => {
  const t = TRANSLATIONS[lang];

  // Sliders
  // computeExponent: 24 = 10^24 FLOPs, up to 30 = 10^30 FLOPs
  const [computeExp, setComputeExp] = useState<number>(26);
  const [gridPowerGW, setGridPowerGW] = useState<number>(5);

  const presets = [
    { label: 'GPT-4 (2023)', exp: 25, gw: 1 },
    { label: 'Llama-3 (2024)', exp: 26, gw: 2.5 },
    { label: 'Agent Swarm (2025)', exp: 27, gw: 5 },
    { label: 'Full Exascale ASI (2026)', exp: 29, gw: 15 }
  ];

  // Calculations
  const stats = useMemo(() => {
    // 10^24 FLOPs ~ 20 MW for silicon cluster
    // Each order of magnitude scales silicon exponentially
    const powerMultiplier = Math.pow(10, computeExp - 24);
    const siliconMW = 20 * powerMultiplier;
    const siliconGW = siliconMW / 1000;
    
    // Nuclear plants needed (each 1.1 GW AP1000)
    const nuclearPlants = +(siliconGW / 1.1).toFixed(1);
    
    // Evaporative cooling water: ~0.5 gallons per kWh
    // Gallons/hour = (siliconMW * 1000 kW) * 0.5
    const waterGallonsPerHour = Math.round(siliconMW * 500);

    // Metric tons CO2 / year (assuming typical grid 380g CO2/kWh)
    const carbonTonsPerYear = Math.round((siliconMW * 8760 * 380) / 1000);

    // Biological Wetware equivalent:
    // Human brain is 10^18 FLOPs at 20W. 
    // Scaling biology: 10^24 FLOPs is roughly 100W of CL-1 arrays
    // Each 10x compute requires only ~3x biological neuron density
    const wetwareWatts = Math.round(20 * Math.pow(3, computeExp - 24));
    const wetwareLitresPerDay = +(0.15 * Math.pow(2.2, computeExp - 24)).toFixed(2);
    const biologicalNeurons = Math.round(800000 * Math.pow(4, computeExp - 24));

    const efficiencyRatio = Math.round((siliconMW * 1000000) / Math.max(1, wetwareWatts));

    const gridDeficit = siliconGW > gridPowerGW;

    return {
      siliconMW,
      siliconGW,
      nuclearPlants,
      waterGallonsPerHour,
      carbonTonsPerYear,
      wetwareWatts,
      wetwareLitresPerDay,
      biologicalNeurons,
      efficiencyRatio,
      gridDeficit
    };
  }, [computeExp, gridPowerGW]);

  const applyPreset = (exp: number, gw: number) => {
    audioSynth.playChirp(720);
    setComputeExp(exp);
    setGridPowerGW(gw);
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden border-cyan-500/20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-400">
                <Zap size={18} />
              </span>
              <h2 className="text-xl font-bold text-white tracking-wide">
                {lang === 'gu' ? 'થર્મોડાયનેમિક અડચણ કેલ્ક્યુલેટર' : 'The Thermodynamic Bottleneck Calculator'}
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              {lang === 'gu' 
                ? 'સિલિકોન ડેટા સેન્ટરના 5 ગીગાવોટ વીજળી અને પાણીના વપરાશની તુલના 20 વોટના માનવ મગજ અને CL-1 વેટવેર સાથે કરો.' 
                : 'Compute scale is colliding headfirst into the planetary electric grid. Compare silicon cooling demands against the 20W biological wetware paradigm.'}
            </p>
          </div>

          {/* Presets */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400">Presets:</span>
            {presets.map((p) => (
              <button
                key={p.label}
                onClick={() => applyPreset(p.exp, p.gw)}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono transition-all border ${
                  computeExp === p.exp
                    ? 'bg-amber-500/20 border-amber-400 text-amber-300 shadow-glow-amber'
                    : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-white hover:border-slate-500'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Interactive Controls & Dual Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Sliders Panel */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-cyan-500/15 pb-3">
            <h3 className="text-sm font-bold font-mono uppercase text-slate-200 flex items-center gap-2">
              <Sliders size={16} className="text-cyan-400" />
              Simulation Parameters
            </h3>
            <span className="text-xs font-mono text-cyan-400">Real-Time Model</span>
          </div>

          {/* Slider 1: Target Compute Scale */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-300 font-medium">Target Compute Scale:</span>
              <span className="text-cyan-300 font-bold px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/40">
                10^{computeExp} FLOPs
              </span>
            </div>
            <input 
              type="range"
              min={24}
              max={30}
              step={1}
              value={computeExp}
              onChange={(e) => {
                audioSynth.playNeuronSpike(400 + (Number(e.target.value) - 24) * 50);
                setComputeExp(Number(e.target.value));
              }}
              className="w-full accent-cyan-400 cursor-pointer h-2 bg-slate-800 rounded-lg"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>10^24 (Llama-2)</span>
              <span>10^27 (Frontier)</span>
              <span>10^30 (Planetary ASI)</span>
            </div>
          </div>

          {/* Slider 2: Available Grid Power */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-300 font-medium">Grid Power Allocation:</span>
              <span className="text-amber-300 font-bold px-2 py-0.5 rounded bg-amber-950/60 border border-amber-500/40">
                {gridPowerGW} GW
              </span>
            </div>
            <input 
              type="range"
              min={0.5}
              max={25}
              step={0.5}
              value={gridPowerGW}
              onChange={(e) => {
                audioSynth.playChirp(500 + Number(e.target.value) * 15);
                setGridPowerGW(Number(e.target.value));
              }}
              className="w-full accent-amber-400 cursor-pointer h-2 bg-slate-800 rounded-lg"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>0.5 GW (Small Grid)</span>
              <span>5 GW (Meta Hyperion)</span>
              <span>25 GW (Mega Cluster)</span>
            </div>
          </div>

          {/* Thermodynamic Alert Banner if grid exceeded */}
          {stats.gridDeficit ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold">
                <AlertTriangle size={15} />
                <span>GRID COLLAPSE WARNING: {(stats.siliconGW - gridPowerGW).toFixed(1)} GW DEFICIT</span>
              </div>
              <p className="text-[11px] text-rose-300/80 leading-relaxed">
                Silicon compute demands ({stats.siliconGW.toFixed(1)} GW) exceed regional transmission limits. Rolling brownouts or dedicated private nuclear power plants are mandatory.
              </p>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold">
                <Leaf size={15} />
                <span>GRID CAPACITY STABLE ({(gridPowerGW - stats.siliconGW).toFixed(1)} GW HEADROOM)</span>
              </div>
              <p className="text-[11px] text-emerald-300/80 leading-relaxed">
                Regional grid currently handles the load, but cooling water consumption remains critically high.
              </p>
            </div>
          )}

          {/* Efficiency Multiplier Callout */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/20 text-center">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
              Biological Energy Advantage
            </span>
            <div className="text-3xl font-extrabold font-mono text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-amber-300 mt-1">
              {stats.efficiencyRatio.toLocaleString()}x
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Fewer Joules consumed per synaptic tensor multiplication.
            </p>
          </div>
        </div>

        {/* Real-time Side-by-Side Comparison */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
          
          {/* SILICON ROUTE CARD */}
          <div className="glass-panel glass-panel-alert rounded-2xl p-5 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between border-b border-rose-500/20 pb-2.5">
                <div className="flex items-center gap-2">
                  <Factory size={18} className="text-rose-400" />
                  <h4 className="text-sm font-bold text-rose-300 uppercase tracking-wide">
                    Silicon Route
                  </h4>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  GPU / TPU Clusters
                </span>
              </div>

              <div className="mt-4 space-y-4">
                <div>
                  <span className="text-[11px] font-mono text-slate-400">Total Power Consumption:</span>
                  <div className="text-2xl font-bold font-mono text-rose-200">
                    {stats.siliconGW >= 1 ? `${stats.siliconGW.toFixed(2)} GW` : `${stats.siliconMW.toLocaleString()} MW`}
                  </div>
                  <span className="text-[10px] text-slate-400">Electricity drawn from grid 24/7</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Droplet size={12} className="text-sky-400" />
                    Evaporative Cooling Water:
                  </span>
                  <div className="text-lg font-bold font-mono text-sky-300">
                    {stats.waterGallonsPerHour.toLocaleString()} gal / hr
                  </div>
                  <span className="text-[10px] text-slate-400">Consumed to prevent thermal throttling</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Zap size={12} className="text-amber-400" />
                    Nuclear Reactor Equivalent:
                  </span>
                  <div className="text-lg font-bold font-mono text-amber-300">
                    {stats.nuclearPlants} AP1000 Units (1.1 GW)
                  </div>
                  <span className="text-[10px] text-slate-400">Dedicated nuclear reactors required</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Flame size={12} className="text-rose-400" />
                    Annual Carbon Emission:
                  </span>
                  <div className="text-base font-bold font-mono text-rose-300">
                    ~{stats.carbonTonsPerYear.toLocaleString()} Tons CO2/yr
                  </div>
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-500/20 text-[11px] font-mono text-rose-300 text-center">
              Thermodynamic Limit: Heat density prevents further physical miniaturization
            </div>
          </div>

          {/* BIOLOGICAL WETWARE (CL-1) ROUTE CARD */}
          <div className="glass-panel rounded-2xl p-5 border-cyan-500/30 flex flex-col justify-between space-y-4 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-36 h-36 bg-cyan-500/10 rounded-full blur-2xl"></div>
            <div>
              <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2.5">
                <div className="flex items-center gap-2">
                  <Dna size={18} className="text-cyan-400" />
                  <h4 className="text-sm font-bold text-cyan-300 uppercase tracking-wide">
                    Wetware Route (CL-1)
                  </h4>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  Living Neurons on MEA
                </span>
              </div>

              <div className="mt-4 space-y-4">
                <div>
                  <span className="text-[11px] font-mono text-slate-400">Total Power Consumption:</span>
                  <div className="text-2xl font-bold font-mono text-cyan-300 flex items-baseline gap-2">
                    {stats.wetwareWatts.toLocaleString()} Watts
                    <span className="text-[11px] font-normal text-emerald-400">(-99.999%)</span>
                  </div>
                  <span className="text-[10px] text-slate-400">Operates at biological 37.0°C homeostatic baseline</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Droplet size={12} className="text-emerald-400" />
                    Nutrient Perfusion Solution:
                  </span>
                  <div className="text-lg font-bold font-mono text-emerald-300">
                    {stats.wetwareLitresPerDay} Litres / Day
                  </div>
                  <span className="text-[10px] text-slate-400">Glucose and electrolyte microfluidic feed</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Activity size={12} className="text-cyan-400" />
                    Living Human Neurons:
                  </span>
                  <div className="text-lg font-bold font-mono text-cyan-200">
                    ~{stats.biologicalNeurons.toLocaleString()} Cells
                  </div>
                  <span className="text-[10px] text-slate-400">Cultured in-vitro on silicon CMOS arrays</span>
                </div>

                <div>
                  <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                    <Leaf size={12} className="text-emerald-400" />
                    Environmental Impact:
                  </span>
                  <div className="text-base font-bold font-mono text-emerald-400">
                    Near Zero Carbon Footprint
                  </div>
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-cyan-950/40 border border-cyan-500/30 text-[11px] font-mono text-cyan-300 text-center shadow-glow-cyan">
              Biological Advantage: Massively parallel Hebbian plasticity in 3D volume
            </div>
          </div>

        </div>

      </div>

      {/* Dynamic Comparison Curve Chart (SVG) */}
      <div className="glass-panel rounded-2xl p-6 border-cyan-500/20">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold font-mono uppercase text-slate-200">
              Exponential Energy Cost vs Compute Scale (The 2026 Wall)
            </h3>
            <p className="text-xs text-slate-400">
              Silicon energy demands shoot vertically into the Gigawatt domain while biological wetware remains virtually flat.
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="w-3 h-0.5 bg-rose-400 inline-block"></span>
              Silicon Route (MW/GW)
            </span>
            <span className="flex items-center gap-1.5 text-cyan-400">
              <span className="w-3 h-0.5 bg-cyan-400 inline-block"></span>
              CL-1 Wetware (Watts)
            </span>
          </div>
        </div>

        {/* SVG Curve */}
        <div className="relative w-full h-56 bg-slate-950/60 rounded-xl border border-cyan-500/15 p-4 flex items-center justify-center">
          <svg className="w-full h-full" viewBox="0 0 800 200" preserveAspectRatio="none">
            {/* Grid Lines */}
            <line x1="50" y1="20" x2="780" y2="20" stroke="#1e293b" strokeDasharray="4 4" />
            <line x1="50" y1="70" x2="780" y2="70" stroke="#1e293b" strokeDasharray="4 4" />
            <line x1="50" y1="120" x2="780" y2="120" stroke="#1e293b" strokeDasharray="4 4" />
            <line x1="50" y1="170" x2="780" y2="170" stroke="#334155" strokeWidth="1.5" />
            
            {/* Silicon Wall Curve (Exponential rise) */}
            <path 
              d="M 60 165 Q 350 160, 520 120 T 750 25" 
              fill="none" 
              stroke="#FF2A6D" 
              strokeWidth="3.5"
              filter="drop-shadow(0 0 8px rgba(255,42,109,0.8))"
            />

            {/* Wetware Line (Virtually flat efficient line) */}
            <path 
              d="M 60 168 Q 400 166, 750 162" 
              fill="none" 
              stroke="#00F2FE" 
              strokeWidth="3.5"
              filter="drop-shadow(0 0 8px rgba(0,242,254,0.8))"
            />

            {/* Silicon Wall Indicator */}
            <line x1="550" y1="15" x2="550" y2="175" stroke="#FFB300" strokeDasharray="3 3" strokeWidth="1.5" />
            <text x="555" y="40" fill="#FFB300" fontSize="11" fontFamily="JetBrains Mono">5GW Grid Wall</text>

            {/* Point on silicon */}
            <circle cx="680" cy="55" r="5" fill="#FF2A6D" className="animate-ping" />
            <circle cx="680" cy="55" r="5" fill="#FF2A6D" />

            {/* Point on wetware */}
            <circle cx="680" cy="163" r="5" fill="#00F2FE" className="animate-pulse" />
          </svg>
        </div>
      </div>

    </div>
  );
};
