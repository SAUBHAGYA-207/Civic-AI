import {
  ReportDetail,
  PaginatedReports,
  DashboardSummary,
  HotspotItem,
  WorkflowStatus,
} from '../types';

export const DEFAULT_TUNNEL_API = 'https://manuals-shorts-downtown-pill.trycloudflare.com/api';

export function getApiBase(): string {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('civicpulse_api_base');
    if (stored && stored.trim()) {
      return stored.trim().replace(/\/+$/, '');
    }
    // If accessing via localhost or 127.0.0.1, use /api proxy
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return '/api';
    }
    // On Vercel, default to the active live Cloudflare tunnel
    return DEFAULT_TUNNEL_API;
  }
  return DEFAULT_TUNNEL_API;
}

export function setApiBase(url: string): void {
  if (!url || !url.trim()) {
    localStorage.removeItem('civicpulse_api_base');
  } else {
    localStorage.setItem('civicpulse_api_base', url.trim().replace(/\/+$/, ''));
  }
}

async function safeFetchJson<T>(url: string, options?: RequestInit, fallbackData?: T): Promise<T> {
  try {
    const res = await fetch(url, options);
    const contentType = res.headers.get('content-type') || '';

    // If server returned HTML (e.g. Vercel SPA rewrite when backend is not running on cloud)
    if (contentType.includes('text/html') || !contentType.includes('application/json')) {
      if (fallbackData !== undefined) {
        return fallbackData;
      }
      throw new Error(
        'The backend API is unreachable at this URL. ' +
        'Please verify that your Cloudflare tunnel and local backend server are active.'
      );
    }

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    if (fallbackData !== undefined) {
      return fallbackData;
    }
    throw err;
  }
}

export async function createReport(formData: FormData): Promise<{ report_id: string; processing_status: string; message: string }> {
  const base = getApiBase();
  const res = await fetch(`${base}/reports`, {
    method: 'POST',
    body: formData,
  });

  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('text/html')) {
    throw new Error(
      'Cannot submit report: Backend server is unreachable at ' + base
    );
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to submit report (${res.status})`);
  }
  return res.json();
}

export async function analyzeReport(reportId: string): Promise<ReportDetail> {
  const base = getApiBase();
  return safeFetchJson<ReportDetail>(`${base}/reports/${reportId}/analyze`, {
    method: 'POST',
  });
}

export async function getReport(reportId: string): Promise<ReportDetail> {
  const base = getApiBase();
  return safeFetchJson<ReportDetail>(`${base}/reports/${reportId}`);
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

  const base = getApiBase();
  return safeFetchJson<PaginatedReports>(
    `${base}/reports?${q.toString()}`,
    {},
    { total: 0, page: 1, limit: 15, items: [] }
  );
}

export async function updateReportStatus(
  reportId: string,
  newStatus: WorkflowStatus,
  actorId: string,
  reason: string,
  reviewerToken: string
): Promise<ReportDetail> {
  const base = getApiBase();
  return safeFetchJson<ReportDetail>(`${base}/reports/${reportId}/updates`, {
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
}

const DEFAULT_SUMMARY: DashboardSummary = {
  total_reports: 0,
  reports_awaiting_review: 0,
  reports_urgent_review: 0,
  reports_in_progress: 0,
  reports_resolved: 0,
  reports_clarification_requested: 0,
  reports_overdue: 0,
  category_distribution: {},
  pathway_distribution: {},
  avg_response_time_hours: null,
  median_response_time_hours: null,
};

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const base = getApiBase();
  return safeFetchJson<DashboardSummary>(
    `${base}/dashboard/summary`,
    {},
    DEFAULT_SUMMARY
  );
}

export async function getHotspots(): Promise<HotspotItem[]> {
  const base = getApiBase();
  return safeFetchJson<HotspotItem[]>(`${base}/dashboard/hotspots`, {}, []);
}

export async function getSystemHealth(): Promise<any> {
  const base = getApiBase();
  return safeFetchJson<any>(
    `${base}/dashboard/health`,
    {},
    {
      service: 'CivicPulse AI Backend',
      status: 'offline',
      ollama: {
        status: 'unreachable',
        error: 'Backend API is currently offline or unreachable at ' + base,
      },
    }
  );
}
