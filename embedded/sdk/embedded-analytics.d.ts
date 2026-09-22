/**
 * Embedded Analytics JavaScript SDK - TypeScript Definitions
 */

export interface EmbedTokenRequest {
  dashboardId?: string;
  chartId?: string;
  expiresIn?: number;
  domain?: string;
}

export interface EmbedTokenResponse {
  token: string;
  expiresAt: string;
  embedUrl: string;
}

export interface Dashboard {
  id: string;
  title: string;
  description?: string;
  charts: ChartConfig[];
  createdAt: string;
  updatedAt: string;
}

export interface ChartConfig {
  chartId: string;
  title?: string;
  width?: number;
  height?: number;
}

export interface Chart {
  id: string;
  title: string;
  chartType: string;
  query: string;
  config: ChartOptions;
  createdAt: string;
  updatedAt: string;
}

export interface ChartOptions {
  fill?: boolean;
  tension?: number;
  beginAtZero?: boolean;
  [key: string]: unknown;
}

export interface ChartData {
  chartId: string;
  data: Record<string, unknown>[];
  columns: string[];
  updatedAt: string;
}

export interface EmbeddedAnalyticsConfig {
  apiBase: string;
  defaultTokenExpiry?: number;
}

export interface EmbedOptions {
  container: string | HTMLElement;
  embedUrl: string;
  width?: string | number;
  height?: string | number;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

export class EmbeddedAnalytics {
  constructor(config: EmbeddedAnalyticsConfig);
  
  createToken(request: EmbedTokenRequest): Promise<EmbedTokenResponse>;
  listDashboards(): Promise<Dashboard[]>;
  getDashboard(dashboardId: string): Promise<Dashboard>;
  listCharts(): Promise<Chart[]>;
  getChart(chartId: string): Promise<Chart>;
  getChartData(chartId: string, token: string): Promise<ChartData>;
  embedDashboard(options: EmbedOptions): HTMLIFrameElement;
  embedChart(options: EmbedOptions): HTMLIFrameElement;
  createAndEmbedDashboard(
    container: string | HTMLElement,
    dashboardId: string,
    options?: Partial<EmbedOptions>
  ): Promise<HTMLIFrameElement>;
  createAndEmbedChart(
    container: string | HTMLElement,
    chartId: string,
    options?: Partial<EmbedOptions>
  ): Promise<HTMLIFrameElement>;
  refreshToken(iframe: HTMLIFrameElement, request: EmbedTokenRequest): Promise<void>;
}

export function createEmbeddedAnalyticsHook(analytics: EmbeddedAnalytics): () => EmbeddedAnalytics;

declare global {
  interface Window {
    __DEWP_EMBEDDED_CONFIG__?: EmbeddedAnalyticsConfig;
    DEWPEmbeddedAnalytics?: EmbeddedAnalytics;
  }
}

export default EmbeddedAnalytics;