export type Resume = {
  id: string;
  original_filename: string;
  file_size_bytes: number;
  created_at: string;
};

export type ParsedProfile = {
  resume_id: string;
  skills: string[];
  projects: {
    name: string;
    description?: string | null;
    technologies?: string[];
  }[];
  experience: {
    title: string;
    company?: string | null;
    duration?: string | null;
    description?: string | null;
  }[];
  technologies: string[];
  education: {
    institution: string;
    degree?: string | null;
    year?: string | null;
  }[];
  achievements: string[];
  parser_name: string;
  parse_status: "pending" | "completed" | "failed";
  parse_error?: string | null;
};

export type ParseProgressEvent = {
  stage: string;
  percent: number;
  message: string;
  result?: ParsedProfile;
};
