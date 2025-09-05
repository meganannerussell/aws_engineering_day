/**
 * TypeScript interfaces for Smart Text Analytics Pipeline JSON output
 * AWS Engineering Day Hackathon 2024
 *
 * Use these interfaces to ensure type safety when working with the pipeline output
 */

export interface ProjectMetadata {
  project_title: string;
  question_text: string;
  total_responses: number;
  processing_time_seconds: number;
  timestamp: string; // ISO 8601 format
  processing_id: string;
  services_used: {
    comprehend_pii: boolean;
    comprehend_sentiment: boolean;
    bedrock_embeddings: boolean;
    bedrock_llm: boolean;
  };
  quality_metrics: {
    pii_detected_count: number;
    responses_clustered: number;
    clustering_confidence: number;
    avg_sentiment_confidence: number;
  };
}

export interface SummaryStats {
  total_topics: number;
  avg_responses_per_topic: number;
  overall_sentiment_distribution: SentimentDistribution;
  overall_sentiment_score: number;
  pii_detection_rate: number;
  most_common_pii_types: string[];
}

export interface SentimentDistribution {
  positive: number;
  neutral: number;
  negative: number;
  mixed: number;
}

export interface SentimentScores {
  Positive: number;
  Negative: number;
  Neutral: number;
  Mixed: number;
}

export interface TopicExample {
  response_id: string;
  text: string;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
  confidence: number;
}

export interface TrendData {
  previous_period_count: number;
  change_percentage: number;
  sentiment_trend: 'improving' | 'declining' | 'stable';
}

export interface Topic {
  topic_id: string;
  label: string;
  count: number;
  percentage: number;
  sentiment_mean: number;
  sentiment_confidence: number;
  sentiment_distribution: SentimentDistribution;
  key_themes: string[];
  examples: TopicExample[];
  trend_data: TrendData;
}

export interface TopicAssignment {
  topic_id: string;
  topic_label: string;
  confidence_score: number;
}

export interface SentimentAnalysis {
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
  confidence: number;
  scores: SentimentScores;
}

export interface ResponseMetadata {
  word_count: number;
  character_count: number;
  processing_timestamp: string; // ISO 8601 format
}

export interface Response {
  response_id: string;
  original_text: string;
  clean_text: string;
  topic_assignment: TopicAssignment;
  multi_topic_assignments: TopicAssignment[];
  sentiment: SentimentAnalysis;
  pii_detected: boolean;
  pii_types: string[];
  metadata: ResponseMetadata;
}

export interface ChartDataPoint {
  label: string;
  value: number;
  percentage: number;
  color: string;
}

export interface SentimentOverviewPoint {
  sentiment: string;
  count: number;
  percentage: number;
  color: string;
}

export interface SentimentByTopic {
  topic: string;
  positive: number;
  neutral: number;
  negative: number;
  sentiment_score: number;
}

export interface TimelineTopicData {
  count: number;
  sentiment: number;
}

export interface TimelineData {
  period: string;
  topics: Record<string, TimelineTopicData>;
}

export interface ChartData {
  topic_distribution: ChartDataPoint[];
  sentiment_overview: SentimentOverviewPoint[];
  sentiment_by_topic: SentimentByTopic[];
  timeline_data: TimelineData[];
}

export interface ExportFormats {
  csv_download_url: string;
  excel_download_url: string;
  powerpoint_download_url: string;
}

export interface ApiInfo {
  version: string;
  generated_at: string; // ISO 8601 format
  request_id: string;
  processing_region: string;
}

export interface SmartTextAnalyticsOutput {
  project_metadata: ProjectMetadata;
  summary_stats: SummaryStats;
  topics: Topic[];
  responses: Response[];
  chart_data: ChartData;
  export_formats: ExportFormats;
  api_info: ApiInfo;
}

// Utility types for common use cases
export type SentimentType = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
export type PIIType = 'EMAIL' | 'PHONE' | 'NAME' | 'ADDRESS' | 'SSN' | 'CREDIT_DEBIT_NUMBER';
export type TrendType = 'improving' | 'declining' | 'stable';

// Helper interfaces for component props
export interface TopicCardProps {
  topic: Topic;
  showExamples?: boolean;
  showTrend?: boolean;
}

export interface SentimentBadgeProps {
  sentiment: SentimentType;
  confidence: number;
  size?: 'small' | 'medium' | 'large';
}

export interface ChartProps {
  data: ChartDataPoint[] | SentimentOverviewPoint[] | SentimentByTopic[];
  height?: number;
  showLegend?: boolean;
  interactive?: boolean;
}

// Filter and sort options
export interface TopicFilters {
  minCount?: number;
  maxCount?: number;
  sentimentRange?: [number, number];
  searchTerm?: string;
  piiOnly?: boolean;
}

export interface TopicSortOptions {
  field: 'count' | 'sentiment_mean' | 'label' | 'percentage';
  direction: 'asc' | 'desc';
}

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  meta?: {
    timestamp: string;
    request_id: string;
    processing_time_ms: number;
  };
}

// Commonly used API responses
export type AnalyticsApiResponse = ApiResponse<SmartTextAnalyticsOutput>;
export type TopicsApiResponse = ApiResponse<Topic[]>;
export type ResponsesApiResponse = ApiResponse<Response[]>;

// Real-time updates (if implementing WebSocket/SSE)
export interface ProcessingUpdate {
  processing_id: string;
  stage: 'pii_detection' | 'embeddings' | 'clustering' | 'labeling' | 'sentiment' | 'complete';
  progress_percentage: number;
  estimated_completion_seconds?: number;
  current_step_description: string;
}

// Configuration for pipeline execution
export interface PipelineConfig {
  max_responses?: number;
  clustering_min_size?: number;
  enable_pii_detection?: boolean;
  enable_multi_topic?: boolean;
  sentiment_threshold?: number;
  language?: string;
}

// Export all types as a namespace for easier importing
export namespace SmartAnalytics {
  export type Output = SmartTextAnalyticsOutput;
  export type Topic = Topic;
  export type Response = Response;
  export type ChartData = ChartData;
  export type SentimentType = SentimentType;
  export type PIIType = PIIType;
}
