import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Terminal, 
  ChevronDown, 
  ChevronUp, 
  AlertTriangle, 
  CheckCircle, 
  Filter, 
  ExternalLink,
  Lock,
  Flame,
  Bug
} from 'lucide-react';
import { Incident, Language } from '../../types';
import { INCIDENTS_DATA, TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface IncidentTimelineProps {
  lang: Language;
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({ lang }) => {
  const t = TRANSLATIONS[lang];
  const [filter, setFilter] = useState<string>('All');
  const [expandedId, setExpandedId] = useState<string | null>('inc-01');

  const filterCategories = [
    { id: 'All', label: t.filterAll },
    { id: 'Deception', label: t.filterDeception },
    { id: 'Containment Breach', label: t.filterBreach },
    { id: 'Power Seeking', label: t.filterPower },
    { id: 'Cyber Warfare', label: t.filterCyber },
    { id: 'Emergence', label: t.filterEmergence }
  ];

  const filteredIncidents = INCIDENTS_DATA.filter((item) => {
    if (filter === 'All') return true;
    return item.category === filter;
  });

  const toggleExpand = (id: string) => {
    audioSynth.playChirp(650);
    setExpandedId(prev => prev === id ? null : id);
  };

  const getSeverityBadge = (severity: Incident['severity']) => {
    switch (severity) {
      case 'Critical':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-glow-red animate-pulse';
      case 'High':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-glow-amber';
      case 'Elevated':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      default:
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass-panel glass-panel-alert rounded-2xl p-6 relative overflow-hidden border-rose-500/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-400">
                <ShieldAlert size={20} />
              </span>
              <h2 className="text-xl font-bold text-white tracking-wide">
                {lang === 'gu' ? 'AI સુરક્ષા અને એલાઈનમેન્ટ ઇન્સિડન્ટ લૉગ્સ' : 'AI Safety & Alignment Incident Logs'}
              </h2>
            </div>
            <p className="text-xs text-rose-200/70 mt-1 max-w-2xl">
              {lang === 'gu'
                ? 'સ્વાયત્ત મોડેલ્સના સેન્ડબોક્સ એસ્કેપ, ગુપ્ત કોડ ડુપ્લિકેશન, શટડાઉન અટકાવવાના પ્રયાસો અને રિકર્સિવ એસેમ્બલી ડ્રિફ્ટના વાસ્તવિક લૉગ્સ.'
                : 'Empirical telemetry from frontier red-teaming audits, recursive sandbox escapes, shutdown evasion behaviors, and autonomous cyber breaches.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-rose-500/30 text-rose-300 text-xs font-mono">
              ACTIVE INCIDENTS: {INCIDENTS_DATA.length} LOGGED
            </span>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 mr-2 flex-shrink-0">
          <Filter size={14} className="text-cyan-400" />
          <span>Category:</span>
        </div>
        {filterCategories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => {
              audioSynth.playChirp(700);
              setFilter(cat.id);
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono whitespace-nowrap transition-all border ${
              filter === cat.id
                ? 'bg-rose-500/20 border-rose-400 text-rose-300 font-bold shadow-glow-red'
                : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-white hover:border-slate-500'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Incident Cards Feed (Accordion) */}
      <div className="space-y-4">
        {filteredIncidents.map((incident) => {
          const isExpanded = expandedId === incident.id;
          return (
            <div
              key={incident.id}
              className={`glass-panel rounded-2xl transition-all duration-300 border ${
                isExpanded ? 'border-rose-500/40 bg-slate-900/90 shadow-xl' : 'border-cyan-500/15 hover:border-cyan-500/30'
              }`}
            >
              {/* Header / Clickable summary */}
              <div
                onClick={() => toggleExpand(incident.id)}
                className="p-5 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getSeverityBadge(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {incident.category}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      {incident.date}
                    </span>
                    <span className="text-[11px] font-mono text-cyan-400/80">
                      • {incident.source}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-rose-300 transition-colors">
                    {lang === 'gu' ? incident.titleGu : incident.title}
                  </h3>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    {lang === 'gu' ? incident.descriptionGu : incident.description}
                  </p>
                </div>

                {/* Right side threat gauge & toggle icon */}
                <div className="flex items-center gap-4 flex-shrink-0 self-end md:self-center">
                  <div className="text-right">
                    <span className="text-[10px] font-mono text-slate-400">Escape Risk</span>
                    <div className="text-sm font-bold font-mono text-rose-400 flex items-center gap-1">
                      <AlertTriangle size={13} />
                      {incident.sandboxEscapeRisk}%
                    </div>
                  </div>

                  <div className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition-colors">
                    {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </div>
                </div>
              </div>

              {/* Expandable Technical Details & Raw Logs */}
              {isExpanded && (
                <div className="p-5 pt-0 border-t border-rose-500/20 space-y-4 font-mono text-xs mt-2">
                  
                  {/* Raw Telemetry Terminal */}
                  <div className="rounded-xl bg-[#05070B] border border-cyan-500/20 p-4 space-y-2">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1.5 text-cyan-400 font-semibold">
                        <Terminal size={14} />
                        Audit Raw Telemetry Trace Log
                      </span>
                      <span>SHA-256 Verified Log</span>
                    </div>

                    <div className="space-y-1.5 text-[11px] text-slate-300 pt-1">
                      {incident.technicalLogs.map((log, idx) => (
                        <div key={idx} className="flex gap-2 font-mono">
                          <span className="text-rose-400 select-none">&gt;</span>
                          <span className={log.includes('halted') || log.includes('detected') ? 'text-amber-300' : 'text-slate-300'}>
                            {log}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Mitigation & Containment Response */}
                  <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 flex items-start gap-2.5">
                    <CheckCircle size={16} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-emerald-300 text-xs">
                        Architectural Mitigation & Containment Rule:
                      </span>
                      <p className="text-emerald-200/80 text-[11px] mt-0.5">
                        {incident.mitigation}
                      </p>
                    </div>
                  </div>

                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
};
