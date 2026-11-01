import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, PlusCircle, Search, ListFilter, Settings, CheckCircle2, AlertTriangle, RefreshCw, X } from 'lucide-react';
import { getSystemHealth, getApiBase, setApiBase, DEFAULT_TUNNEL_API } from '../api/client';

interface NavbarProps {
  activeTab: 'report' | 'dashboard' | 'track' | 'list';
  setActiveTab: (tab: 'report' | 'dashboard' | 'track' | 'list') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'degraded'>('checking');
  const [showSettings, setShowSettings] = useState(false);
  const [apiUrl, setApiUrl] = useState(getApiBase());
  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);

  const checkHealth = () => {
    setHealthStatus('checking');
    getSystemHealth()
      .then((data) => {
        setHealthStatus(data.status === 'operational' ? 'healthy' : 'degraded');
      })
      .catch(() => {
        setHealthStatus('degraded');
      });
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const handleSaveEndpoint = async (e: React.FormEvent) => {
    e.preventDefault();
    setTesting(true);
    setTestResult(null);
    setApiBase(apiUrl);

    try {
      const data = await getSystemHealth();
      if (data.status === 'operational') {
        setHealthStatus('healthy');
        setTestResult('Successfully connected to CivicPulse Backend & Local Ollama!');
      } else {
        setHealthStatus('degraded');
        setTestResult('Connected to backend, but Ollama models are not ready. Ensure Ollama is running.');
      }
    } catch (err: any) {
      setHealthStatus('degraded');
      setTestResult(`Connection failed: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  return (
    <>
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

            {/* Health status badge & connection settings */}
            <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
              <button
                onClick={() => setShowSettings(true)}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-slate-700 transition"
                title="Configure Backend Connection"
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    healthStatus === 'healthy'
                      ? 'bg-emerald-500 animate-pulse'
                      : healthStatus === 'checking'
                      ? 'bg-amber-400 animate-ping'
                      : 'bg-rose-500'
                  }`}
                />
                <span className="hidden sm:inline">
                  {healthStatus === 'healthy' ? 'Ollama Online' : healthStatus === 'checking' ? 'Checking AI...' : 'Ollama Offline'}
                </span>
                <Settings className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Backend Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-blue-600" />
                <h3 className="text-base font-bold text-slate-900">Backend & Ollama Connection</h3>
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-4">
              <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-200 text-xs text-blue-900 leading-relaxed">
                <strong>Why is Ollama local?</strong> CivicPulse AI processes sensitive civic grievances using local open-weight models (<strong>Qwen2.5-VL:3B</strong> and <strong>Qwen2.5:1.5B</strong>) to ensure zero citizen data leaks to commercial cloud APIs.
              </div>

              <form onSubmit={handleSaveEndpoint} className="space-y-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Backend API Base URL</label>
                  <input
                    type="text"
                    required
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    placeholder="e.g. http://localhost:8000/api or /api"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>

                <div className="flex flex-wrap gap-2 text-[11px]">
                  <span className="text-slate-400 py-1">Presets:</span>
                  <button
                    type="button"
                    onClick={() => setApiUrl(DEFAULT_TUNNEL_API)}
                    className="px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 font-mono font-bold"
                  >
                    Cloudflare Live Tunnel
                  </button>
                  <button
                    type="button"
                    onClick={() => setApiUrl('http://localhost:8000/api')}
                    className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono"
                  >
                    http://localhost:8000/api
                  </button>
                  <button
                    type="button"
                    onClick={() => setApiUrl('/api')}
                    className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono"
                  >
                    /api (Relative)
                  </button>
                </div>

                {testResult && (
                  <div
                    className={`p-3 rounded-xl text-xs flex items-start gap-2 ${
                      testResult.includes('Successfully')
                        ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {testResult.includes('Successfully') ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                    )}
                    <span>{testResult}</span>
                  </div>
                )}

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowSettings(false)}
                    className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                  >
                    Close
                  </button>
                  <button
                    type="submit"
                    disabled={testing}
                    className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold transition flex items-center gap-1.5"
                  >
                    {testing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : null}
                    <span>Save & Test Connection</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
