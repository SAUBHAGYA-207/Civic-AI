import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Building2,
  Clock,
  ArrowRight,
  ShieldAlert,
  Loader2,
  UserCheck,
  Eye,
  FileText,
  Layers,
  MapPin,
  Calendar,
} from 'lucide-react';
import { getReport, analyzeReport, updateReportStatus } from '../api/client';
import { ReportDetail, WorkflowStatus } from '../types';
import { StatusBadge, PathwayBadge } from '../components/StatusBadge';
import { ProvenanceBadge } from '../components/ProvenanceBadge';

interface EvidenceAnalysisPageProps {
  reportId: string;
  onBack: () => void;
  onNavigateTrack: (id: string) => void;
}

export const EvidenceAnalysisPage: React.FC<EvidenceAnalysisPageProps> = ({
  reportId,
  onBack,
  onNavigateTrack,
}) => {
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reviewer status update state
  const [newStatus, setNewStatus] = useState<WorkflowStatus>('in_progress');
  const [reviewerId, setReviewerId] = useState('officer_patna_central');
  const [reviewerReason, setReviewerReason] = useState('');
  const [reviewerToken, setReviewerToken] = useState('civicpulse-reviewer-dev-key-secure');
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateMessage, setUpdateMessage] = useState<string | null>(null);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getReport(reportId);
      setReport(data);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to load report');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      const updated = await analyzeReport(reportId);
      setReport(updated);
      setAnalyzing(false);
    } catch (err: any) {
      setError(err.message || 'Analysis pipeline failed');
      setAnalyzing(false);
    }
  };

  const handleReviewerUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewerReason.trim()) {
      alert('Please specify a reason for this status change.');
      return;
    }
    try {
      setUpdateLoading(true);
      setUpdateMessage(null);
      const updated = await updateReportStatus(
        reportId,
        newStatus,
        reviewerId.trim(),
        reviewerReason.trim(),
        reviewerToken.trim()
      );
      setReport(updated);
      setUpdateMessage('Status successfully updated and recorded in the audit history.');
      setReviewerReason('');
      setUpdateLoading(false);
    } catch (err: any) {
      alert(`Update failed: ${err.message}`);
      setUpdateLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center">
        <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-3" />
        <p className="text-sm font-semibold text-slate-600">Retrieving grievance record and evidence...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800">
          <h2 className="text-lg font-bold mb-2">Error Loading Report</h2>
          <p className="text-sm mb-4">{error || 'Report not found.'}</p>
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-lg bg-white border border-rose-300 text-rose-700 font-semibold text-sm hover:bg-rose-100/50"
          >
            ← Return to Previous Page
          </button>
        </div>
      </div>
    );
  }

  const evidenceRecord = report.evidence_record;
  const imageEv = evidenceRecord?.image_evidence;
  const textEv = evidenceRecord?.text_evidence;
  const fusedEv = evidenceRecord?.fused_evidence;
  const triage = report.triage_decision;
  const dept = report.department_recommendation;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-6 border-b border-slate-200">
        <div>
          <button onClick={onBack} className="text-xs font-semibold text-blue-600 hover:text-blue-800 mb-2 flex items-center gap-1">
            ← Back to Listing
          </button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 font-mono">
              #{report.id.slice(0, 8)}...
            </h1>
            <StatusBadge status={report.workflow_status} />
            <PathwayBadge pathway={report.review_pathway} />
          </div>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-3">
            <span>Submitted: {new Date(report.created_at).toLocaleString()}</span>
            {report.address_or_landmark && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-slate-400" />
                {report.address_or_landmark}
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {!evidenceRecord && (
            <button
              onClick={handleRunAnalysis}
              disabled={analyzing}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition shadow-sm disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing Local Qwen Models...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Multimodal AI Analysis</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={() => onNavigateTrack(report.id)}
            className="px-4 py-2.5 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold text-sm transition"
          >
            Public Tracking View
          </button>
        </div>
      </div>

      {/* Citizen Complaint & Attached Photos */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            <FileText className="w-4 h-4 text-blue-600" />
            Citizen Grievance Text (Untrusted Input)
          </div>
          <p className="text-slate-800 text-sm sm:text-base leading-relaxed whitespace-pre-line bg-slate-50 rounded-xl p-4 border border-slate-200">
            "{report.complaint_text}"
          </p>

          {report.latitude && report.longitude && (
            <div className="mt-4 flex items-center gap-2 text-xs text-slate-600 bg-blue-50/50 p-2.5 rounded-lg border border-blue-100">
              <MapPin className="w-4 h-4 text-blue-600 flex-shrink-0" />
              <span>
                Coordinates: <strong>{report.latitude}, {report.longitude}</strong>
              </span>
            </div>
          )}
        </div>

        {/* Photos Preview */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
            <Eye className="w-4 h-4 text-blue-600" />
            Submitted Visual Evidence ({report.attachments.length})
          </div>
          {report.attachments.length > 0 ? (
            <div className="space-y-3">
              {report.attachments.map((att) => (
                <div key={att.id} className="rounded-xl overflow-hidden border border-slate-200 bg-slate-100">
                  <img
                    src={att.url}
                    alt={att.filename}
                    className="w-full h-44 object-cover hover:scale-105 transition duration-300"
                  />
                  <div className="p-2 text-[11px] text-slate-500 bg-white border-t border-slate-200 flex justify-between">
                    <span className="truncate max-w-[150px]">{att.filename}</span>
                    <span>{(att.file_size / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-400 text-xs bg-slate-50 rounded-xl border border-dashed border-slate-200">
              No photograph submitted with this complaint.
            </div>
          )}
        </div>
      </div>

      {/* AI Extraction & Evidence Section (If Available) */}
      {evidenceRecord ? (
        <div className="space-y-6">
          {/* Triage & Department Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Triage Review Pathway */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Recommended Workflow Pathway
                </span>
                <PathwayBadge pathway={triage?.recommended_pathway || null} />
              </div>
              <p className="text-xs text-slate-600 mb-4">
                Determined by deterministic Python rules ({triage?.rule_version}). AI models do NOT assign danger scores.
              </p>
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-700">Triggered Rule Codes:</div>
                <div className="flex flex-wrap gap-1.5">
                  {triage?.reason_codes.map((code, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded text-xs font-mono font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      {code}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Department Recommendation */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Department Recommendation
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">
                  {dept?.department_status === 'recommended' ? 'Recommended' : 'Needs Verification'}
                </span>
              </div>
              <div className="text-base font-bold text-slate-900 mb-1 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-blue-600" />
                {dept?.department_name}
              </div>
              <p className="text-xs text-slate-600 mb-3">{dept?.rationale}</p>
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-800 flex items-start gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Legal Disclaimer:</strong> This is an algorithmic suggestion based on local guidelines. It is NOT an official dispatch or verified governmental referral.
                </span>
              </div>
            </div>
          </div>

          {/* Conflict & Corroboration Callouts */}
          {fusedEv && (
            <div className="space-y-4">
              {fusedEv.conflicts.length > 0 && (
                <div className="bg-rose-50 border border-rose-200 rounded-2xl p-5 text-rose-900">
                  <div className="flex items-center gap-2 font-bold text-sm mb-2 text-rose-800">
                    <ShieldAlert className="w-5 h-5 text-rose-600" />
                    Evidence Conflicts Detected
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-xs text-rose-800">
                    {fusedEv.conflicts.map((conf, idx) => (
                      <li key={idx}>{conf}</li>
                    ))}
                  </ul>
                </div>
              )}

              {fusedEv.corroborations.length > 0 && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 text-emerald-900">
                  <div className="flex items-center gap-2 font-bold text-sm mb-2 text-emerald-800">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    Corroborated Evidence Points
                  </div>
                  <ul className="list-disc list-inside space-y-1 text-xs text-emerald-800">
                    {fusedEv.corroborations.map((corr, idx) => (
                      <li key={idx}>{corr}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Granular Evidence Items with Provenance */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-blue-600" />
                <h2 className="text-base font-bold text-slate-900">Provenance-Tracked Evidence Items</h2>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-600 border border-slate-200">
                Data Sufficiency: {fusedEv?.data_sufficiency.toUpperCase()}
              </span>
            </div>

            <p className="text-xs text-slate-500 mb-4">
              Each atomic observation is mapped to its exact source and verification state to prevent AI hallucinations from masquerading as verified facts.
            </p>

            <div className="divide-y divide-slate-100">
              {fusedEv?.evidence.map((item, idx) => (
                <div key={idx} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="space-y-0.5">
                    <div className="text-xs font-bold text-slate-700 capitalize">
                      {item.field.replace(/_/g, ' ')}
                    </div>
                    <div className="text-sm text-slate-900">{item.value}</div>
                    {item.notes && <div className="text-[11px] text-slate-400 italic">{item.notes}</div>}
                  </div>
                  <div className="flex-shrink-0">
                    <ProvenanceBadge status={item.status} source={item.source} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Unknowns & Limitations */}
          {fusedEv && fusedEv.unknowns.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6">
              <div className="flex items-center gap-2 font-bold text-sm text-slate-800 mb-2">
                <HelpCircle className="w-4 h-4 text-slate-500" />
                Unresolved Unknowns & Assessment Limitations
              </div>
              <ul className="list-disc list-inside space-y-1 text-xs text-slate-600">
                {fusedEv.unknowns.map((unk, idx) => (
                  <li key={idx}>{unk}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Model Transparency & Runtime Metrics */}
          <div className="p-4 rounded-xl bg-slate-100/70 border border-slate-200 text-xs text-slate-500 flex flex-wrap gap-4 justify-between items-center">
            <div>
              <strong>Vision Model:</strong> {evidenceRecord.model_identifiers?.vision_model || 'None'}
            </div>
            <div>
              <strong>Text Model:</strong> {evidenceRecord.model_identifiers?.text_model}
            </div>
            <div>
              <strong>Vision Duration:</strong> {evidenceRecord.model_identifiers?.image_extraction_duration_sec}s
            </div>
            <div>
              <strong>Text Duration:</strong> {evidenceRecord.model_identifiers?.text_extraction_duration_sec}s
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-8 text-center">
          <Sparkles className="w-10 h-10 text-blue-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900 mb-1">AI Evidence Extraction Pending</h3>
          <p className="text-sm text-slate-600 max-w-lg mx-auto mb-6">
            Click below to execute the local multimodal pipeline. Qwen2.5-VL will inspect visual observations, Qwen2.5 will isolate citizen claims, and deterministic rules will route the complaint.
          </p>
          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold transition shadow-md shadow-blue-500/20 disabled:opacity-50"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Running Local Qwen Models...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Execute Analysis Pipeline</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Reviewer Action & State Transition Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <UserCheck className="w-5 h-5 text-indigo-600" />
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Authorized Reviewer Action Panel</h2>
        </div>
        <p className="text-xs text-slate-500 mb-6">
          Authorized municipal case workers can update the complaint state. All changes are immutably recorded in the audit trail.
        </p>

        {updateMessage && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{updateMessage}</span>
          </div>
        )}

        <form onSubmit={handleReviewerUpdate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Target Workflow Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as WorkflowStatus)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs bg-white"
              >
                <option value="awaiting_review">Awaiting Review</option>
                <option value="in_progress">In Progress (Work crew dispatched)</option>
                <option value="clarification_requested">Clarification Requested (Citizen contact needed)</option>
                <option value="resolved">Resolved (Work completed & verified)</option>
                <option value="rejected">Rejected (Out of jurisdiction or invalid)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Reviewer Identifier / Badge ID</label>
              <input
                type="text"
                required
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                placeholder="e.g. officer_patna_101"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Administrative Secret Key</label>
              <input
                type="password"
                required
                value={reviewerToken}
                onChange={(e) => setReviewerToken(e.target.value)}
                placeholder="Reviewer secret token"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Reason for Status Change <span className="text-rose-600">*</span></label>
              <input
                type="text"
                required
                value={reviewerReason}
                onChange={(e) => setReviewerReason(e.target.value)}
                placeholder="e.g. Assigned to Ward 10 road repair crew for patching"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs"
              />
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={updateLoading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-sm disabled:opacity-50"
            >
              {updateLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Recording Status Update...</span>
                </>
              ) : (
                <>
                  <UserCheck className="w-3.5 h-3.5" />
                  <span>Record Authorized Reviewer Action</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
