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
  status: string;
  phase: string;
  current_question: ExecutionQuestion | null;
  previous_questions: ExecutionQuestion[];
}

export interface SubmitAnswerResponse extends ExecutionSnapshot {}
