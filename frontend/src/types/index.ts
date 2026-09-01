export interface VisualizationPayload {
  type: "bar" | "line" | "pie" | "area" | "kpi" | "table";
  figure: {
    data: any[];
    layout: Record<string, any>;
  };
  title?: string;
}

export interface ForecastRecord {
  date: string;
  predicted_value: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
}

export interface ForecastPayload {
  metric: string;
  time_column: string;
  horizon: number;
  predictions: ForecastRecord[];
  confidence_intervals?: {
    levels: number[];
  };
  figure?: {
    data: any[];
    layout: Record<string, any>;
  };
}

export interface QueryResponse {
  conversation_id: string;
  question: string;
  answer: string;
  sql?: string | null;
  data: Record<string, any>[];
  columns: string[];
  insights: string[];
  visualization?: VisualizationPayload | null;
  forecast?: ForecastPayload | null;
  execution_time_ms: number;
  error?: string | null;
}

export interface MessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  response?: QueryResponse;
  loading?: boolean;
}

export interface ConversationSummary {
  id: string;
  title: string;
  lastUpdated: string;
  messageCount: number;
}

export interface DatabaseSourceInfo {
  database_id: string;
  name: string;
  source_type: "mysql" | "sqlite" | "csv" | "excel" | "sql_dump" | "custom_uri";
  tables_count: number;
  tables: string[];
  created_at: string;
  is_default: boolean;
}
