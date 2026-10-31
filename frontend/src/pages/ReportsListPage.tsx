import React, { useState, useEffect } from 'react';
import { Filter, Search, ArrowRight, Loader2, Camera, MapPin, RefreshCw } from 'lucide-react';
import { listReports } from '../api/client';
import { ReportSummaryItem, IssueCategory, ReviewPathway, WorkflowStatus } from '../types';
import { StatusBadge, PathwayBadge } from '../components/StatusBadge';

interface ReportsListPageProps {
  onSelectReport: (id: string) => void;
}

export const ReportsListPage: React.FC<ReportsListPageProps> = ({ onSelectReport }) => {
  const [reports, setReports] = useState<ReportSummaryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState<string>('all');
  const [pathway, setPathway] = useState<string>('all');
  const [status, setStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  const fetchList = async () => {
    try {
      setLoading(true);
      const data = await listReports({
        page,
        limit: 15,
        category,
        pathway,
        status,
      });
      setReports(data.items);
      setTotal(data.total);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchList();
  }, [page, category, pathway, status]);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Public Grievance Ledger</h1>
          <p className="text-slate-600 mt-1 text-sm">
            Auditable list of civic infrastructure reports processed by the platform.
          </p>
        </div>
        <button
          onClick={fetchList}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-wider pr-2 border-r border-slate-200">
          <Filter className="w-4 h-4 text-blue-600" />
          Filters
        </div>

        {/* Category */}
        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-700"
        >
          <option value="all">All Categories</option>
          <option value="road_damage">Road Damage</option>
          <option value="water_leakage">Water Leakage</option>
          <option value="drainage">Drainage & Sewerage</option>
          <option value="waste_management">Waste Management</option>
          <option value="streetlight">Streetlight</option>
          <option value="other">Other</option>
          <option value="unknown">Unknown</option>
        </select>

        {/* Pathway */}
        <select
          value={pathway}
          onChange={(e) => { setPathway(e.target.value); setPage(1); }}
          className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-700"
        >
          <option value="all">All Pathways</option>
          <option value="urgent_human_review">Urgent Human Review</option>
          <option value="human_review">Human Review</option>
          <option value="request_clarification">Request Clarification</option>
          <option value="standard_triage">Standard Triage</option>
        </select>

        {/* Status */}
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-700"
        >
          <option value="all">All Workflow Statuses</option>
          <option value="submitted">Submitted</option>
          <option value="under_analysis">Under Analysis</option>
          <option value="awaiting_review">Awaiting Review</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="clarification_requested">Clarification Requested</option>
          <option value="rejected">Rejected</option>
        </select>

        <span className="text-xs text-slate-400 ml-auto">
          Showing {reports.length} of {total} reports
        </span>
      </div>

      {/* Reports Table / Card List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="py-16 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-2" />
            <p className="text-xs text-slate-500">Loading grievances...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-sm">
            No grievance reports matched the selected filters.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {reports.map((r) => (
              <div
                key={r.id}
                onClick={() => onSelectReport(r.id)}
                className="p-4 sm:p-5 hover:bg-slate-50/80 transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono font-bold text-xs text-blue-700">#{r.id.slice(0, 8)}</span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 capitalize">
                      {r.issue_category.replace(/_/g, ' ')}
                    </span>
                    {r.has_image && (
                      <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        <Camera className="w-3 h-3 text-slate-400" /> Photo attached
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-slate-600 flex flex-wrap items-center gap-3">
                    {r.address_or_landmark ? (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        {r.address_or_landmark}
                      </span>
                    ) : (
                      <span className="italic text-slate-400">No landmark specified</span>
                    )}
                    <span>•</span>
                    <span>Logged: {new Date(r.created_at).toLocaleDateString()}</span>
                    {r.department_name && (
                      <>
                        <span>•</span>
                        <span className="text-slate-700 font-medium">{r.department_name}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center flex-shrink-0">
                  <PathwayBadge pathway={r.review_pathway} />
                  <StatusBadge status={r.workflow_status} />
                  <ArrowRight className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {total > 15 && (
        <div className="flex justify-between items-center text-xs text-slate-600">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="px-3 py-1.5 rounded-lg border border-slate-300 disabled:opacity-40"
          >
            Previous Page
          </button>
          <span>Page {page} of {Math.ceil(total / 15)}</span>
          <button
            disabled={page >= Math.ceil(total / 15)}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 disabled:opacity-40"
          >
            Next Page
          </button>
        </div>
      )}
    </div>
  );
};
