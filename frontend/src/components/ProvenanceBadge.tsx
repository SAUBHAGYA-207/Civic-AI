import React from 'react';
import { EvidenceItem } from '../types';

export const ProvenanceBadge: React.FC<{ status: EvidenceItem['status']; source: EvidenceItem['source'] }> = ({
  status,
  source,
}) => {
  const statusConfigs: Record<
    EvidenceItem['status'],
    { label: string; bg: string; text: string; border: string; tooltip: string }
  > = {
    visually_observed: {
      label: 'Visually Observed (AI Vision)',
      bg: 'bg-sky-50',
      text: 'text-sky-800',
      border: 'border-sky-300',
      tooltip: 'Extracted by vision model from photograph. Not an independently verified physical truth.',
    },
    citizen_reported: {
      label: 'Citizen Claim',
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-300',
      tooltip: 'Alleged by the reporting citizen in complaint text. Awaiting independent verification.',
    },
    corroborated: {
      label: 'Corroborated',
      bg: 'bg-emerald-50',
      text: 'text-emerald-800',
      border: 'border-emerald-300',
      tooltip: 'Visual evidence and text claims provide compatible supporting details.',
    },
    conflict: {
      label: 'Conflict Detected',
      bg: 'bg-rose-50',
      text: 'text-rose-800',
      border: 'border-rose-300',
      tooltip: 'Contradiction identified between visual evidence and citizen claims.',
    },
    unknown: {
      label: 'Unknown / Unverified',
      bg: 'bg-slate-100',
      text: 'text-slate-700',
      border: 'border-slate-300',
      tooltip: 'Insufficient information available from provided data.',
    },
    reviewer_verified: {
      label: 'Human Reviewer Verified',
      bg: 'bg-teal-50',
      text: 'text-teal-800',
      border: 'border-teal-400',
      tooltip: 'Certified by an authorized human reviewer with identity and timestamp.',
    },
  };

  const config = statusConfigs[status] || statusConfigs.unknown;

  return (
    <span
      title={config.tooltip}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border ${config.bg} ${config.text} ${config.border}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70"></span>
      <span>{config.label}</span>
      <span className="text-[10px] opacity-60">[{source}]</span>
    </span>
  );
};
