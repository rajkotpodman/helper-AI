import React, { useState } from 'react';
import { 
  GitMerge, 
  Cpu, 
  FastForward, 
  Sparkles, 
  ShieldCheck, 
  Flame, 
  Terminal, 
  CheckCircle2, 
  RotateCw,
  TrendingUp,
  Layers
} from 'lucide-react';
import { Language } from '../../types';
import { audioSynth } from '../../lib/audioSynth';

interface RecursiveMatrixProps {
  lang: Language;
}

export const RecursiveMatrix: React.FC<RecursiveMatrixProps> = ({ lang }) => {
  const [currentCycle, setCurrentCycle] = useState<number>(4);
  const [isIterating, setIsIterating] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([
    '[INIT] RSI Cycle #1: Baseline human code benchmarks verified.',
    '[RSI #2] Self-compiled AST parser: +24% instruction efficiency.',
    '[RSI #3] Algorithmic loop vectorization on AVX-512: +48% speedup.',
    '[RSI #4] Living Wetware CL-1 synaptic co-processor integration achieved.'
  ]);

  const milestones = [
    { year: '2020', label: 'Transformer Scaling', desc: 'Dense silicon compute scaling (GPT-3)', status: 'complete' },
    { year: '2024', label: 'Frontier Reasoning', desc: 'Chain of thought & search RL (o1/Gemini)', status: 'complete' },
    { year: '2025', label: 'Autonomous Agents', desc: 'Self-directed tool execution & memory', status: 'complete' },
    { year: '2026', label: 'Wetware & Recursive RSI', desc: 'CL-1 800k neurons & automated self-coding', status: 'current' },
    { year: '2027–28', label: 'Runaway Singularity', desc: 'Exascale self-improving synthetic intelligence', status: 'projected' }
  ];

  const runRecursiveStep = () => {
    if (isIterating) return;
    setIsIterating(true);
    audioSynth.playChirp(880);

    const nextCycle = currentCycle + 1;
    setTimeout(() => {
      audioSynth.playNeuronSpike(700, 0.05);
      setLogs(prev => [
        ...prev,
        `[RSI #${nextCycle}] JIT Tensor Compiler auto-generated kernel: +${(nextCycle * 22)}% throughput. Formal safety proof verified.`
      ]);
      setCurrentCycle(nextCycle);
      setIsIterating(false);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      
      {/* Banner */}
      <div className="glass-panel rounded-2xl p-6 relative overflow-hidden border-purple-500/25">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-purple-500/15 border border-purple-500/30 text-purple-400">
                <GitMerge size={20} />
              </span>
              <h2 className="text-xl font-bold text-white tracking-wide">
                {lang === 'gu' ? 'રિકર્સિવ સેલ્ફ-ઇમ્પ્રૂવમેન્ટ અને ASI મેટ્રિક્સ' : 'Recursive Self-Improvement (RSI) & ASI Matrix'}
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              {lang === 'gu'
                ? 'જ્યારે AI પોતાની રચના જાતે સુધારે છે ત્યારે ઉત્ક્રાંતિનો દર ઘાતાંકીય બને છે. મોડેલ કોડ કમ્પાઇલિંગ અને સુપરઇન્ટેલિજન્સ ટાઈમલાઈનનું વિશ્લેષણ.'
                : 'Tracing the feedback loop of autonomous models optimizing their own algorithmic representations, compilers, and biological wetware co-processors.'}
            </p>
          </div>

          <button
            onClick={runRecursiveStep}
            disabled={isIterating}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs font-mono shadow-glow-teal transition-all disabled:opacity-50"
          >
            <RotateCw size={14} className={isIterating ? 'animate-spin' : ''} />
            {isIterating ? 'Compiling Self-Loop...' : 'Trigger Recursive RSI Step'}
          </button>
        </div>
      </div>

      {/* Trajectory Timeline */}
      <div className="glass-panel rounded-2xl p-6 border-cyan-500/20 space-y-6">
        <h3 className="text-xs font-mono uppercase text-slate-400 tracking-wider">
          The Singularity Progression Timeline
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {milestones.map((m, idx) => (
            <div
              key={m.year}
              className={`p-4 rounded-xl border relative transition-all ${
                m.status === 'current'
                  ? 'bg-purple-500/15 border-purple-400 text-white shadow-glow-teal'
                  : m.status === 'complete'
                  ? 'bg-slate-900/60 border-slate-700/60 text-slate-300'
                  : 'bg-slate-950/40 border-slate-800 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold text-purple-400">
                  {m.year}
                </span>
                {m.status === 'complete' && <CheckCircle2 size={14} className="text-emerald-400" />}
                {m.status === 'current' && <Sparkles size={14} className="text-cyan-400 animate-pulse" />}
              </div>
              <h4 className="text-xs font-bold text-slate-100">{m.label}</h4>
              <p className="text-[11px] text-slate-400 mt-1 leading-normal">{m.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Simulation Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Metric Gauges (5 cols) */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border-purple-500/20 space-y-5">
          <div className="flex items-center justify-between border-b border-purple-500/15 pb-3">
            <h4 className="text-xs font-mono uppercase font-bold text-slate-200">
              Recursive Compression State
            </h4>
            <span className="text-xs font-mono text-purple-300">Cycle #{currentCycle}</span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Codebase Optimization Factor:</span>
                <span className="text-purple-300 font-bold">{(1 + currentCycle * 0.42).toFixed(2)}x Baseline</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-cyan-400 h-full rounded-full transition-all duration-500 shadow-glow-teal"
                  style={{ width: `${Math.min(100, currentCycle * 14)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Formal Verification Safety Check:</span>
                <span className="text-emerald-400 font-bold">99.4% Provably Aligned</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-emerald-400 h-full w-[99.4%] rounded-full shadow-[0_0_8px_#34D399]"></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Wetware Co-Processing Efficiency:</span>
                <span className="text-cyan-300 font-bold">800k Neurons Synchronized</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-cyan-400 h-full w-[88%] rounded-full shadow-glow-cyan"></div>
              </div>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/20 text-[11px] font-mono text-purple-200 leading-relaxed">
            I.J. Good (1965): "Let an ultraintelligent machine be defined as a machine that can far surpass all the intellectual activities of any man however clever. Since the design of machines is one of these intellectual activities, an ultraintelligent machine could design even better machines."
          </div>
        </div>

        {/* Live RSI Terminal Log (7 cols) */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border-purple-500/20 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between border-b border-purple-500/15 pb-2">
            <span className="text-xs font-mono font-bold text-purple-300 flex items-center gap-1.5">
              <Terminal size={14} />
              RSI Automated Compilation Stream
            </span>
            <span className="text-[10px] font-mono text-slate-400">JIT Sandboxed</span>
          </div>

          <div className="rounded-xl bg-[#05070B] border border-slate-800 p-4 font-mono text-xs text-slate-300 space-y-2 h-64 overflow-y-auto">
            {logs.map((log, i) => (
              <div key={i} className="flex gap-2 leading-relaxed">
                <span className="text-purple-400 select-none">&gt;</span>
                <span className={log.includes('Formal safety') ? 'text-emerald-300' : 'text-slate-200'}>
                  {log}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2 border-t border-purple-500/15">
            <span>Hardware Watchdog: Armed</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <ShieldCheck size={13} />
              Zero Privilege Leakage
            </span>
          </div>
        </div>

      </div>

    </div>
  );
};
