import React from 'react';
import { WorkflowStatus, ReviewPathway } from '../types';

export const StatusBadge: React.FC<{ status: WorkflowStatus }> = ({ status }) => {
  const configs: Record<WorkflowStatus, { label: string; bg: string; text: string; border: string }> = {
    submitted: { label: 'Submitted', bg: 'bg-slate-100', text: 'text-slate-800', border: 'border-slate-300' },
    under_analysis: { label: 'Under Analysis', bg: 'bg-indigo-50', text: 'text-indigo-800', border: 'border-indigo-300' },
    awaiting_review: { label: 'Awaiting Review', bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-300' },
    in_progress: { label: 'In Progress', bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-300' },
    resolved: { label: 'Resolved', bg: 'bg-emerald-50', text: 'text-emerald-800', border: 'border-emerald-300' },
    rejected: { label: 'Rejected', bg: 'bg-rose-50', text: 'text-rose-800', border: 'border-rose-300' },
    clarification_requested: { label: 'Clarification Requested', bg: 'bg-purple-50', text: 'text-purple-800', border: 'border-purple-300' },
  };

  const c = configs[status] || { label: status, bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-300' };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      {c.label}
    </span>
  );
};

export const PathwayBadge: React.FC<{ pathway: ReviewPathway | null }> = ({ pathway }) => {
  if (!pathway) return <span className="text-xs text-slate-400 italic">Not evaluated</span>;

  const configs: Record<ReviewPathway, { label: string; bg: string; text: string; border: string; icon: string }> = {
    urgent_human_review: { label: 'Urgent Human Review', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-300', icon: '🚨' },
    human_review: { label: 'Human Review', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-300', icon: '👤' },
    request_clarification: { label: 'Request Clarification', bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-300', icon: '❓' },
    standard_triage: { label: 'Standard Triage', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-300', icon: '📋' },
  };

  const c = configs[pathway] || { label: pathway, bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-300', icon: 'ℹ️' };

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      <span>{c.icon}</span>
      <span>{c.label}</span>
    </span>
  );
};
