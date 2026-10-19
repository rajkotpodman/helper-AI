import React from 'react';
import { 
  LayoutDashboard, 
  Dna, 
  Zap, 
  GitMerge, 
  ShieldAlert, 
  Headphones, 
  Bot,
  ChevronLeft,
  ChevronRight,
  Flame,
  Cpu
} from 'lucide-react';
import { NavigationSection, Language } from '../../types';
import { TRANSLATIONS } from '../../lib/constants';
import { audioSynth } from '../../lib/audioSynth';

interface SidebarProps {
  currentSection: NavigationSection;
  onSelectSection: (section: NavigationSection) => void;
  collapsed: boolean;
  onToggleCollapsed: () => void;
  lang: Language;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentSection,
  onSelectSection,
  collapsed,
  onToggleCollapsed,
  lang,
  mobileOpen,
  onCloseMobile
}) => {
  const t = TRANSLATIONS[lang];

  const navItems = [
    {
      id: 'overview' as NavigationSection,
      label: t.navOverview,
      icon: LayoutDashboard,
      badge: 'LIVE',
      badgeColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30'
    },
    {
      id: 'wetware' as NavigationSection,
      label: t.navWetware,
      icon: Dna,
      badge: 'CL-1',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    },
    {
      id: 'thermodynamics' as NavigationSection,
      label: t.navThermodynamics,
      icon: Zap,
      badge: '20W/5GW',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30'
    },
    {
      id: 'recursive' as NavigationSection,
      label: t.navRecursive,
      icon: GitMerge,
      badge: 'ASI',
      badgeColor: 'text-purple-400 bg-purple-500/10 border-purple-500/30'
    },
    {
      id: 'safety' as NavigationSection,
      label: t.navSafety,
      icon: ShieldAlert,
      badge: '5 LOGS',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/30'
    },
    {
      id: 'audio' as NavigationSection,
      label: t.navAudio,
      icon: Headphones,
      badge: '3 EPISODES',
      badgeColor: 'text-sky-400 bg-sky-500/10 border-sky-500/30'
    },
    {
      id: 'agent' as NavigationSection,
      label: t.navAgent,
      icon: Bot,
      badge: 'CONNECTED',
      badgeColor: 'text-teal-400 bg-teal-500/10 border-teal-500/30'
    }
  ];

  const handleNavClick = (id: NavigationSection) => {
    audioSynth.playChirp(680);
    onSelectSection(id);
    onCloseMobile();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed lg:sticky top-[61px] left-0 z-50 h-[calc(100vh-61px)] transition-all duration-300 ease-in-out border-r border-cyan-500/15 bg-[#080B11]/95 backdrop-blur-xl flex flex-col justify-between ${
          mobileOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0'
        } ${collapsed ? 'lg:w-20' : 'lg:w-72'}`}
      >
        {/* Navigation Links */}
        <div className="p-3 space-y-1.5 overflow-y-auto">
          <div className="flex items-center justify-between px-3 py-2 text-xs font-mono uppercase text-slate-400 tracking-wider">
            {!collapsed && <span>System Navigation</span>}
            <button
              onClick={onToggleCollapsed}
              className="hidden lg:flex p-1.5 rounded-lg bg-slate-900 border border-cyan-500/20 text-slate-400 hover:text-cyan-400 transition-colors ml-auto"
              title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            >
              {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            </button>
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl transition-all duration-200 text-left relative group ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 via-cyan-500/10 to-transparent border border-cyan-400/40 text-cyan-300 shadow-glow-cyan font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                }`}
              >
                {/* Active indicator bar */}
                {isActive && (
                  <span className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-cyan-400 shadow-[0_0_12px_#00F2FE]"></span>
                )}

                <Icon 
                  size={20} 
                  className={`flex-shrink-0 transition-transform group-hover:scale-110 ${
                    isActive ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(0,242,254,0.6)]' : 'text-slate-400'
                  }`} 
                />

                {!collapsed && (
                  <div className="flex-1 flex items-center justify-between min-w-0">
                    <span className="text-xs truncate font-medium tracking-wide">
                      {item.label}
                    </span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${item.badgeColor}`}>
                      {item.badge}
                    </span>
                  </div>
                )}

                {/* Collapsed Tooltip */}
                {collapsed && (
                  <div className="hidden lg:block absolute left-full ml-3 px-2.5 py-1.5 rounded-md bg-slate-900 border border-cyan-500/30 text-xs text-cyan-300 font-mono whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity shadow-xl z-50">
                    {item.label}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Footer Quick Status Box */}
        <div className="p-3 border-t border-cyan-500/15 bg-slate-950/60">
          {!collapsed ? (
            <div className="p-3 rounded-xl bg-slate-900/80 border border-cyan-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Flame size={13} className="text-amber-400" />
                  Thermal State
                </span>
                <span className="text-emerald-400 font-bold">37.0°C (Homeostatic)</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full w-[65%] rounded-full shadow-[0_0_8px_#00F2FE]"></div>
              </div>
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 pt-0.5">
                <span>MEA Density: 800k/cm²</span>
                <span className="text-cyan-300">DishBrain Active</span>
              </div>
            </div>
          ) : (
            <div className="flex justify-center p-2 text-cyan-400">
              <Cpu size={18} className="animate-spin-slow" />
            </div>
          )}
        </div>
      </aside>
    </>
  );
};
