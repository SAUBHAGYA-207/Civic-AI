import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, PlusCircle, Search, ListFilter, AlertCircle } from 'lucide-react';
import { getSystemHealth } from '../api/client';

interface NavbarProps {
  activeTab: 'report' | 'dashboard' | 'track' | 'list';
  setActiveTab: (tab: 'report' | 'dashboard' | 'track' | 'list') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'degraded'>('checking');

  useEffect(() => {
    getSystemHealth()
      .then((data) => {
        setHealthStatus(data.status === 'operational' ? 'healthy' : 'degraded');
      })
      .catch(() => {
        setHealthStatus('degraded');
      });
  }, []);

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('report')}>
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-slate-900 tracking-tight">CivicPulse AI</span>
                <span className="text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 uppercase">
                  Local AI Triage
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">Privacy-conscious infrastructure & grievance triage</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('report')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                activeTab === 'report'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <PlusCircle className="w-4 h-4" />
              <span>Report Issue</span>
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                activeTab === 'dashboard'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Live Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('track')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                activeTab === 'track'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Track Complaint</span>
            </button>

            <button
              onClick={() => setActiveTab('list')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-semibold transition ${
                activeTab === 'list'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <ListFilter className="w-4 h-4" />
              <span>All Reports</span>
            </button>
          </nav>

          {/* Health status badge */}
          <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-slate-200">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                healthStatus === 'healthy'
                  ? 'bg-emerald-500 animate-pulse'
                  : healthStatus === 'checking'
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-rose-500'
              }`}
            />
            <span className="text-xs text-slate-500">
              {healthStatus === 'healthy' ? 'Local Ollama Ready' : healthStatus === 'checking' ? 'Checking AI...' : 'Ollama Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
