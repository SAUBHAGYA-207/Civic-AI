import React, { useState, useEffect } from 'react';
import { Search, Clock, CheckCircle2, AlertCircle, MapPin, Building2, Layers, Loader2, ArrowRight } from 'lucide-react';
import { getReport } from '../api/client';
import { ReportDetail } from '../types';
import { StatusBadge, PathwayBadge } from '../components/StatusBadge';

interface TrackingPageProps {
  initialReportId?: string | null;
  onNavigateAnalyze: (id: string) => void;
}

export const TrackingPage: React.FC<TrackingPageProps> = ({ initialReportId, onNavigateAnalyze }) => {
  const [searchId, setSearchId] = useState(initialReportId || '');
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async (id: string) => {
    if (!id.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getReport(id.trim());
      setReport(data);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Report not found. Please verify the ID.');
      setReport(null);
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialReportId) {
      fetchReport(initialReportId);
    }
  }, [initialReportId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchReport(searchId);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Track Civic Grievance</h1>
        <p className="text-slate-600 mt-2 text-sm">
          Enter your unique Grievance ID to inspect live resolution progress, status history, and administrative updates.
        </p>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            required
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            placeholder="Paste Complaint UUID (e.g. 3a7b9c1d-4e5f-...)"
            className="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm bg-white"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm transition shadow-sm disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Search</span>}
        </button>
      </form>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {report && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          {/* Header Details */}
          <div className="p-6 sm:p-8 border-b border-slate-200 bg-slate-50/50">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Complaint Reference</span>
                <div className="text-lg sm:text-xl font-mono font-bold text-slate-900 break-all">{report.id}</div>
                <div className="text-xs text-slate-500 mt-1">
                  Submitted on {new Date(report.created_at).toLocaleString()}
                </div>
              </div>

              <div className="flex flex-col sm:items-end gap-2">
                <StatusBadge status={report.workflow_status} />
                <button
                  onClick={() => onNavigateAnalyze(report.id)}
                  className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  <span>View Evidence Breakdown</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <div className="p-6 sm:p-8 space-y-6">
            {/* Complaint Summary */}
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Complaint Narrative</h3>
              <p className="text-sm text-slate-800 bg-slate-50 p-4 rounded-xl border border-slate-200 leading-relaxed whitespace-pre-line">
                "{report.complaint_text}"
              </p>
            </div>

            {/* Department Recommendation */}
            {report.department_recommendation && (
              <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 flex items-start gap-3">
                <Building2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-semibold text-blue-900">Recommended Handling Authority</div>
                  <div className="text-sm font-bold text-blue-950">
                    {report.department_recommendation.department_name}
                  </div>
                  <p className="text-xs text-blue-800/80 mt-1">
                    {report.department_recommendation.rationale}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-2 italic">
                    Note: Recommendation generated for administrative routing. Does not signify official external confirmation.
                  </p>
                </div>
              </div>
            )}

            {/* Status Timeline */}
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-600" />
                Audit Trail & Status Timeline
              </h3>

              <div className="relative pl-6 border-l-2 border-slate-200 space-y-6">
                {report.status_history.map((hist, idx) => (
                  <div key={hist.id} className="relative group">
                    {/* Timeline dot */}
                    <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-blue-600 border-2 border-white shadow" />
                    
                    <div>
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className="font-bold text-slate-900 capitalize">{hist.new_status.replace(/_/g, ' ')}</span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-500 font-mono text-[11px]">{new Date(hist.created_at).toLocaleString()}</span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-500 font-semibold text-[11px]">By: {hist.actor_id} ({hist.actor_type})</span>
                      </div>
                      <p className="text-xs text-slate-700 mt-1 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                        {hist.reason}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
