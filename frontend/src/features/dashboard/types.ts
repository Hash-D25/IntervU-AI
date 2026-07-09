export interface InterviewHistoryItem {
  id: string;
  company_name: string | null;
  target_role: string;
  interview_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  answered_count: number;
  overall_score: number | null;
  has_feedback: boolean;
}

export interface CategoryScore {
  category: string;
  average_score: number;
  answer_count: number;
}

export interface ProgressPoint {
  interview_id: string;
  label: string;
  recorded_at: string;
  overall_score: number;
}

export interface DashboardSummary {
  interview_history: InterviewHistoryItem[];
  strengths: string[];
  weaknesses: string[];
  category_scores: CategoryScore[];
  dimension_averages: Record<string, number>;
  progress_over_time: ProgressPoint[];
  total_interviews: number;
  completed_interviews: number;
}

export interface FeedbackResult {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  learning_roadmap: string[];
  overall_score: number;
  generator_name: string;
}
