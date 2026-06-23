import type { CompetitorGroups, WorkflowConfig } from "./workflow";

export type InterviewMessageRole = "user" | "assistant";

export interface InterviewMessage {
  id?: string;
  role: InterviewMessageRole;
  content: string;
  created_at: string;
}

export interface InterviewInput {
  user_message: string;
  thinking_enabled?: boolean;
  analysis_preferences?: {
    reportLanguage?: "中文" | "英文";
    analysisDepth?: "快速" | "标准" | "深入";
    competitorCount?: 3 | 5 | 8;
    outputFocus?: "功能" | "定价" | "用户反馈" | "全量";
    reportStyle?: "简报型" | "结构化研究型";
  };
}

export interface InterviewSSEMessage {
  token?: string;
  extracted_config?: Partial<WorkflowConfig>;
  suggested_competitors?: string[];
  suggested_competitor_groups?: CompetitorGroups;
  workflow_title?: string;
  is_complete?: boolean;
  response?: string;
}
