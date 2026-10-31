import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Clock,
  CheckCircle2,
  FileText,
  MapPin,
  TrendingUp,
  Inbox,
  Loader2,
  Flame,
} from 'lucide-react';
import { getDashboardSummary, getHotspots } from '../api/client';
import { DashboardSummary, HotspotItem } from '../types';

interface DashboardPageProps {
  onSelectReport?: (id: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [hotspots, setHotspots] = useState<HotspotItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [sumData, hotData] = await Promise.all([
          getDashboardSummary(),
          getHotspots(),
        ]);
        setSummary(sumData);
        setHotspots(hotData);
        setLoading(false);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard data');
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-16 text-center">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-3" />
        <p className="text-sm font-semibold text-slate-600">Querying live database metrics...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="max-w-6xl mx-auto py-12 px-4">
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800">
          <h2 className="text-lg font-bold mb-2">Error Loading Dashboard</h2>
          <p className="text-sm">{error || 'Could not fetch summary data.'}</p>
        </div>
      </div>
    );
  }

  const isEmpty = summary.total_reports === 0;

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Civic Accountability Dashboard</h1>
        <p className="text-slate-600 mt-2 text-sm">
          Real-time metrics computed directly from database records. No synthetic or simulated values.
        </p>
      </div>

      {/* Fresh DB Empty State */}
      {isEmpty && (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
            <Inbox className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-2">Fresh Database Initialized</h3>
          <p className="text-slate-500 text-sm max-w-md mx-auto">
            Zero complaints are currently registered in the database. Submit a complaint from the "Report Issue" tab to view real-time triage metrics.
          </p>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 mb-1">Total Grievances</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">{summary.total_reports}</div>
          <div className="text-[11px] text-slate-400 mt-1">All logged records</div>
        </div>

        {/* Urgent Review */}
        <div className="bg-white rounded-2xl border border-red-200 p-5 shadow-sm bg-red-50/20">
          <div className="text-xs font-semibold text-red-600 mb-1 flex items-center gap-1">
            <Flame className="w-3.5 h-3.5" /> Urgent Review
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-red-700">{summary.reports_urgent_review}</div>
          <div className="text-[11px] text-red-500 mt-1">Hazard / Danger</div>
        </div>

        {/* Awaiting Review */}
        <div className="bg-white rounded-2xl border border-amber-200 p-5 shadow-sm bg-amber-50/20">
          <div className="text-xs font-semibold text-amber-600 mb-1">Awaiting Review</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-700">{summary.reports_awaiting_review}</div>
          <div className="text-[11px] text-amber-500 mt-1">Triage pending</div>
        </div>

        {/* In Progress */}
        <div className="bg-white rounded-2xl border border-blue-200 p-5 shadow-sm bg-blue-50/20">
          <div className="text-xs font-semibold text-blue-600 mb-1">In Progress</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-blue-700">{summary.reports_in_progress}</div>
          <div className="text-[11px] text-blue-500 mt-1">Work crews active</div>
        </div>

        {/* Resolved */}
        <div className="bg-white rounded-2xl border border-emerald-200 p-5 shadow-sm bg-emerald-50/20">
          <div className="text-xs font-semibold text-emerald-600 mb-1">Resolved</div>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">{summary.reports_resolved}</div>
          <div className="text-[11px] text-emerald-500 mt-1">Fixed & verified</div>
        </div>

        {/* Overdue */}
        <div className="bg-white rounded-2xl border border-purple-200 p-5 shadow-sm bg-purple-50/20">
          <div className="text-xs font-semibold text-purple-600 mb-1 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" /> Overdue (&gt;48h)
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-purple-700">{summary.reports_overdue}</div>
          <div className="text-[11px] text-purple-500 mt-1">Action SLA exceeded</div>
        </div>
      </div>

      {/* Charts & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-4">Grievance Distribution by Category</h2>
          {Object.keys(summary.category_distribution).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(summary.category_distribution).map(([cat, count]) => {
                const pct = summary.total_reports > 0 ? ((count / summary.total_reports) * 100).toFixed(0) : '0';
                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-slate-700">
                      <span className="capitalize">{cat.replace(/_/g, ' ')}</span>
                      <span>{count} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-6 text-center">No categorized data yet.</p>
          )}
        </div>

        {/* Pathway Breakdown */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-4">Review Pathway Routing Distribution</h2>
          {Object.keys(summary.pathway_distribution).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(summary.pathway_distribution).map(([path, count]) => {
                const pct = summary.total_reports > 0 ? ((count / summary.total_reports) * 100).toFixed(0) : '0';
                const color =
                  path === 'urgent_human_review'
                    ? 'bg-rose-500'
                    : path === 'human_review'
                    ? 'bg-amber-500'
                    : path === 'request_clarification'
                    ? 'bg-purple-500'
                    : 'bg-emerald-500';

                return (
                  <div key={path} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-slate-700">
                      <span className="capitalize">{path.replace(/_/g, ' ')}</span>
                      <span>{count} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <div className={`${color} h-2 rounded-full transition-all duration-500`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-6 text-center">No pathway evaluations yet.</p>
          )}
        </div>
      </div>

      {/* Response Times & Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Response Time Metrics
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 mb-1">Average Response Time</div>
              <div className="text-xl font-bold text-slate-900">
                {summary.avg_response_time_hours !== null ? `${summary.avg_response_time_hours} hrs` : 'N/A'}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">Creation to first work dispatch</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 mb-1">Median Response Time</div>
              <div className="text-xl font-bold text-slate-900">
                {summary.median_response_time_hours !== null ? `${summary.median_response_time_hours} hrs` : 'N/A'}
              </div>
              <div className="text-[10px] text-slate-400 mt-1">50th percentile resolution speed</div>
            </div>
          </div>
          <p className="text-[11px] text-slate-400 mt-4">
            Calculated solely between initial submission timestamps and authorized transition to 'in_progress' or 'resolved'.
          </p>
        </div>

        {/* Geographic Hotspots */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-rose-600" />
            Geographic Hotspots (Clustered & Anonymized)
          </h2>

          {hotspots.length > 0 ? (
            <div className="divide-y divide-slate-100 max-h-60 overflow-y-auto">
              {hotspots.map((h, idx) => (
                <div key={idx} className="py-2.5 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-slate-800">{h.area_or_cluster}</span>
                    <div className="text-[11px] text-slate-400 capitalize">Category: {h.primary_category.replace(/_/g, ' ')}</div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full font-bold bg-rose-50 text-rose-700 border border-rose-200">
                    {h.count} reports
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-400 text-xs">
              No clustered geographic hotspots identified yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
