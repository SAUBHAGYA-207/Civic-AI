import {
  ReportDetail,
  PaginatedReports,
  DashboardSummary,
  HotspotItem,
  WorkflowStatus,
} from '../types';

const API_BASE = '/api';

export async function createReport(formData: FormData): Promise<{ report_id: string; processing_status: string; message: string }> {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to submit report (${res.status})`);
  }
  return res.json();
}

export async function analyzeReport(reportId: string): Promise<ReportDetail> {
  const res = await fetch(`${API_BASE}/reports/${reportId}/analyze`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed (${res.status})`);
  }
  return res.json();
}

export async function getReport(reportId: string): Promise<ReportDetail> {
  const res = await fetch(`${API_BASE}/reports/${reportId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Report not found (${res.status})`);
  }
  return res.json();
}

export async function listReports(params: {
  page?: number;
  limit?: number;
  category?: string;
  pathway?: string;
  status?: string;
}): Promise<PaginatedReports> {
  const q = new URLSearchParams();
  if (params.page) q.set('page', params.page.toString());
  if (params.limit) q.set('limit', params.limit.toString());
  if (params.category && params.category !== 'all') q.set('category', params.category);
  if (params.pathway && params.pathway !== 'all') q.set('pathway', params.pathway);
  if (params.status && params.status !== 'all') q.set('status', params.status);

  const res = await fetch(`${API_BASE}/reports?${q.toString()}`);
  if (!res.ok) {
    throw new Error(`Failed to list reports (${res.status})`);
  }
  return res.json();
}

export async function updateReportStatus(
  reportId: string,
  newStatus: WorkflowStatus,
  actorId: string,
  reason: string,
  reviewerToken: string
): Promise<ReportDetail> {
  const res = await fetch(`${API_BASE}/reports/${reportId}/updates`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Reviewer-Token': reviewerToken,
    },
    body: JSON.stringify({
      new_status: newStatus,
      actor_type: 'reviewer',
      actor_id: actorId,
      reason: reason,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update status (${res.status})`);
  }
  return res.json();
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard summary (${res.status})`);
  }
  return res.json();
}

export async function getHotspots(): Promise<HotspotItem[]> {
  const res = await fetch(`${API_BASE}/dashboard/hotspots`);
  if (!res.ok) {
    throw new Error(`Failed to fetch hotspots (${res.status})`);
  }
  return res.json();
}

export async function getSystemHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/dashboard/health`);
  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`);
  }
  return res.json();
}
