export interface StockItem {
  ticker: string;
  name: string;
  market: "KOSPI" | "KOSDAQ";
  yf_ticker: string;
}

export interface ElementAnalysis {
  signal: "bullish" | "bearish" | "neutral";
  score: number;
  summary: string;
  key_points: string[];
  data_basis: string[];
  dart_verified?: boolean;
}

export interface AnalysisResult {
  elements: {
    market: ElementAnalysis;
    trend: ElementAnalysis;
    company: ElementAnalysis & { dart_verified?: boolean };
    news: ElementAnalysis;
    candlestick: ElementAnalysis;
    moving_average: ElementAnalysis;
    volume: ElementAnalysis;
    supply_zone: ElementAnalysis;
  };
  overall: {
    score: number;
    recommendation: "매수검토" | "관망" | "매도검토" | "위험";
    summary: string;
    positive_factors: string[];
    risk_factors: string[];
  };
  raw_data: {
    current_price: number;
    change_pct_1d: number;
    position_52w: number;
    ma_aligned: boolean;
    volume_ratio: number;
    dart_available: boolean;
    news_count: number;
    analyzed_at: string;
  };
}

export interface AnalyzeResponse {
  stock: {
    ticker: string;
    name: string;
    current_price: number;
    change_pct_1d: number;
    market_cap?: number;
  };
  analysis: AnalysisResult;
  dart: Record<string, unknown>;
  news: { title: string; date: string; url: string; source: string }[];
  market: Record<string, { value: number; change_pct: number; signal: string }>;
}
