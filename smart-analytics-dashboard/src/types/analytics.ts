export interface ProjectMetadata {
  project_title: string;
  question_text: string;
  total_responses: number;
  processing_time_seconds: number;
  timestamp: string;
  services_used: {
    comprehend_pii: boolean;
    comprehend_sentiment: boolean;
    bedrock_embeddings: boolean;
    bedrock_llm: boolean;
  };
}

export interface SentimentDistribution {
  positive: number;
  negative: number;
  neutral: number;
  mixed: number;
}

export interface Topic {
  topic_id: string;
  label: string;
  count: number;
  sentiment_mean: number;
  sentiment_distribution: SentimentDistribution;
  examples: string[];
}

export interface AnalyticsData {
  project_metadata: ProjectMetadata;
  topics: Topic[];
}

export type ChartType = "bar" | "pie" | "line" | "donut";

export interface ChartConfig {
  type: ChartType;
  data: any[];
  colors?: string[];
}

export interface MetricCard {
  title: string;
  value: string | number;
  description: string;
  icon: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}
