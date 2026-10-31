export type IssueCategory =
  | 'road_damage'
  | 'water_leakage'
  | 'drainage'
  | 'waste_management'
  | 'streetlight'
  | 'other'
  | 'unknown';

export type ReviewPathway =
  | 'urgent_human_review'
  | 'human_review'
  | 'request_clarification'
  | 'standard_triage';

export type WorkflowStatus =
  | 'submitted'
  | 'under_analysis'
  | 'awaiting_review'
  | 'in_progress'
  | 'resolved'
  | 'rejected'
  | 'clarification_requested';

export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface DepartmentRecommendation {
  department_name: string;
  department_status: 'recommended' | 'needs_verification';
  jurisdiction_level: string;
  rationale: string;
  is_official_referral: boolean;
}

export interface TriageDecision {
  rule_version: string;
  recommended_pathway: ReviewPathway;
  reason_codes: string[];
  decision_metadata: Record<string, any>;
  created_at?: string;
}

export interface Attachment {
  id: string;
  filename: string;
  mime_type: string;
  file_size: number;
  url: string;
  created_at: string;
}

export interface StatusHistory {
  id: string;
  previous_status: string | null;
  new_status: string;
  actor_type: string;
  actor_id: string;
  reason: string;
  created_at: string;
}

export interface ImageEvidence {
  issue_candidates: IssueCategory[];
  visible_observations: string[];
  visible_damage_characteristics: string[];
  visible_obstruction_indicators: string[];
  contextual_features: string[];
  image_quality: 'poor' | 'adequate' | 'good' | 'unknown';
  limitations_of_visual_assessment: string[];
  not_visually_verifiable: string[];
  extraction_error?: string | null;
}

export interface TextEvidence {
  issue_category: IssueCategory;
  reported_location: string | null;
  reported_impacts: string[];
  reported_duration: string | null;
  reported_safety_concerns: string[];
  missing_information: string[];
  extraction_error?: string | null;
}

export interface EvidenceItem {
  field: string;
  value: string;
  source: 'image' | 'citizen_text' | 'location_metadata' | 'reviewer';
  status:
    | 'visually_observed'
    | 'citizen_reported'
    | 'corroborated'
    | 'conflict'
    | 'unknown'
    | 'reviewer_verified';
  reviewer_id?: string | null;
  verified_at?: string | null;
  notes?: string | null;
}

export interface FusedEvidence {
  issue_category: IssueCategory;
  evidence: EvidenceItem[];
  conflicts: string[];
  unknowns: string[];
  corroborations: string[];
  requires_human_review: boolean;
  review_reasons: string[];
  data_sufficiency: 'sufficient' | 'partial' | 'insufficient';
}

export interface EvidenceRecord {
  id: string;
  image_evidence: ImageEvidence | null;
  text_evidence: TextEvidence | null;
  fused_evidence: FusedEvidence | null;
  model_identifiers: Record<string, any>;
  schema_version: string;
  created_at: string;
}

export interface ReportDetail {
  id: string;
  complaint_text: string;
  issue_category: IssueCategory;
  latitude: number | null;
  longitude: number | null;
  address_or_landmark: string | null;
  workflow_status: WorkflowStatus;
  review_pathway: ReviewPathway | null;
  department_recommendation: DepartmentRecommendation | null;
  processing_status: ProcessingStatus;
  created_at: string;
  updated_at: string;
  attachments: Attachment[];
  evidence_record: EvidenceRecord | null;
  triage_decision: TriageDecision | null;
  status_history: StatusHistory[];
}

export interface ReportSummaryItem {
  id: string;
  created_at: string;
  issue_category: IssueCategory;
  address_or_landmark: string | null;
  workflow_status: WorkflowStatus;
  review_pathway: ReviewPathway | null;
  department_name: string | null;
  has_image: boolean;
  processing_status: ProcessingStatus;
}

export interface PaginatedReports {
  total: number;
  page: number;
  limit: number;
  items: ReportSummaryItem[];
}

export interface DashboardSummary {
  total_reports: number;
  reports_awaiting_review: number;
  reports_urgent_review: number;
  reports_in_progress: number;
  reports_resolved: number;
  reports_clarification_requested: number;
  reports_overdue: number;
  category_distribution: Record<string, number>;
  pathway_distribution: Record<string, number>;
  avg_response_time_hours: number | null;
  median_response_time_hours: number | null;
}

export interface HotspotItem {
  area_or_cluster: string;
  count: number;
  primary_category: IssueCategory;
  latitude: number | null;
  longitude: number | null;
}
