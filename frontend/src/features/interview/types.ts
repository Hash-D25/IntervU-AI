export type InterviewType = "technical" | "behavioral" | "mixed";

export type InterviewStatus = "created" | "in_progress" | "completed" | "abandoned";

export type ExecutionStatus = "not_started" | "in_progress" | "completed";

export type InterviewSummary = {
  id: string;
  company_name: string | null;
  target_role: string;
  interview_type: InterviewType | null;
  status: InterviewStatus;
  created_at: string;
  updated_at: string;
  answered_count: number;
  overall_score: number | null;
  has_feedback: boolean;
};

export type Interview = {
  id: string;
  user_id: string;
  resume_id: string | null;
  company_name: string | null;
  target_role: string;
  interview_type: InterviewType | null;
  status: InterviewStatus;
  job_description: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateInterviewRequest = {
  resume_id: string;
  company_name: string;
  target_role: string;
  interview_type: InterviewType;
  job_description?: string | null;
};

export interface ExecutionQuestion {
  id: string;
  position: number;
  phase: string;
  text: string;
  category: string;
  difficulty: string;
  answered: boolean;
  answer_transcript?: string | null;
}

export interface ExecutionSnapshot {
  status: ExecutionStatus;
  phase: string;
  current_question: ExecutionQuestion | null;
  previous_questions: ExecutionQuestion[];
}

export type SubmitAnswerResponse = ExecutionSnapshot;
