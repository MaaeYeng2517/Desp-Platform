/**
 * Embedded Analytics JavaScript SDK
 * 
 * Usage:
 * import { EmbeddedAnalytics } from '@dewp/embedded-sdk';
 * 
 * const analytics = new EmbeddedAnalytics({
 *   apiBase: 'http://localhost:8080',
 * });
 * 
 * // Create embed token
 * const token = await analytics.createToken({ dashboardId: 'dashboard-id' });
 * 
 * // Embed dashboard
 * analytics.embedDashboard('container-id', token.embedUrl);
 * 
 * // Embed chart
 * analytics.embedChart('container-id', token.embedUrl);
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
  private apiBase: string;
  private defaultTokenExpiry: number;

  constructor(config: EmbeddedAnalyticsConfig) {
    this.apiBase = config.apiBase.replace(/\/+$/, '');
    this.defaultTokenExpiry = config.defaultTokenExpiry || 3600;
  }

  /**
   * Create an embed token for a dashboard or chart
   */
  async createToken(request: EmbedTokenRequest): Promise<EmbedTokenResponse> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/tokens`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        dashboard_id: request.dashboardId,
        chart_id: request.chartId,
        expires_in: request.expiresIn || this.defaultTokenExpiry,
        domain: request.domain,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Failed to create token' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * List all available dashboards
   */
  async listDashboards(): Promise<Dashboard[]> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/dashboards`);
    if (!response.ok) {
      throw new Error(`Failed to list dashboards: HTTP ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get a specific dashboard
   */
  async getDashboard(dashboardId: string): Promise<Dashboard> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/dashboards/${dashboardId}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Dashboard not found');
      }
      throw new Error(`Failed to get dashboard: HTTP ${response.status}`);
    }
    return response.json();
  }

  /**
   * List all available charts
   */
  async listCharts(): Promise<Chart[]> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/charts`);
    if (!response.ok) {
      throw new Error(`Failed to list charts: HTTP ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get a specific chart
   */
  async getChart(chartId: string): Promise<Chart> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/charts/${chartId}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Chart not found');
      }
      throw new Error(`Failed to get chart: HTTP ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get chart data (requires valid embed token)
   */
  async getChartData(chartId: string, token: string): Promise<ChartData> {
    const response = await fetch(`${this.apiBase}/api/v1/embed/charts/${chartId}/data?embed_token=${token}`);
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Invalid or expired token');
      }
      if (response.status === 403) {
        throw new Error('Token not authorized for this chart');
      }
      throw new Error(`Failed to get chart data: HTTP ${response.status}`);
    }
    return response.json();
  }

  /**
   * Embed a dashboard in an iframe
   */
  embedDashboard(options: EmbedOptions): HTMLIFrameElement {
    const container = typeof options.container === 'string'
      ? document.getElementById(options.container)
      : options.container;

    if (!container) {
      throw new Error(`Container element not found: ${options.container}`);
    }

    const iframe = document.createElement('iframe');
    iframe.src = options.embedUrl;
    iframe.style.width = `${options.width || '100%'}`;
    iframe.style.height = `${options.height || '600px'}`;
    iframe.style.border = 'none';
    iframe.style.borderRadius = '8px';
    iframe.style.backgroundColor = '#f8f9fa';
    iframe.title = 'Embedded Dashboard';
    iframe.allow = 'fullscreen';

    iframe.onload = () => {
      options.onLoad?.();
    };

    iframe.onerror = () => {
      options.onError?.(new Error('Failed to load dashboard'));
    };

    container.innerHTML = '';
    container.appendChild(iframe);

    return iframe;
  }

  /**
   * Embed a chart in an iframe
   */
  embedChart(options: EmbedOptions): HTMLIFrameElement {
    const container = typeof options.container === 'string'
      ? document.getElementById(options.container)
      : options.container;

    if (!container) {
      throw new Error(`Container element not found: ${options.container}`);
    }

    const iframe = document.createElement('iframe');
    iframe.src = options.embedUrl;
    iframe.style.width = `${options.width || '100%'}`;
    iframe.style.height = `${options.height || '400px'}`;
    iframe.style.border = 'none';
    iframe.style.borderRadius = '8px';
    iframe.style.backgroundColor = 'white';
    iframe.title = 'Embedded Chart';
    iframe.allow = 'fullscreen';

    iframe.onload = () => {
      options.onLoad?.();
    };

    iframe.onerror = () => {
      options.onError?.(new Error('Failed to load chart'));
    };

    container.innerHTML = '';
    container.appendChild(iframe);

    return iframe;
  }

  /**
   * Create and embed a dashboard in one call
   */
  async createAndEmbedDashboard(
    container: string | HTMLElement,
    dashboardId: string,
    options: Partial<EmbedOptions> = {}
  ): Promise<HTMLIFrameElement> {
    const token = await this.createToken({ dashboardId });
    return this.embedDashboard({
      container,
      embedUrl: token.embedUrl,
      ...options,
    });
  }

  /**
   * Create and embed a chart in one call
   */
  async createAndEmbedChart(
    container: string | HTMLElement,
    chartId: string,
    options: Partial<EmbedOptions> = {}
  ): Promise<HTMLIFrameElement> {
    const token = await this.createToken({ chartId });
    return this.embedChart({
      container,
      embedUrl: token.embedUrl,
      ...options,
    });
  }

  /**
   * Refresh the embed token for an existing iframe
   */
  async refreshToken(iframe: HTMLIFrameElement, request: EmbedTokenRequest): Promise<void> {
    const token = await this.createToken(request);
    const url = new URL(iframe.src);
    url.searchParams.set('token', token.token);
    iframe.src = url.toString();
  }
}

/**
 * React hook for using Embedded Analytics (for React applications)
 */
export function createEmbeddedAnalyticsHook(analytics: EmbeddedAnalytics) {
  return function useEmbeddedAnalytics() {
    return analytics;
  };
}

// Auto-initialize if global config is present
if (typeof window !== 'undefined' && (window as any).__DEWP_EMBEDDED_CONFIG__) {
  const config = (window as any).__DEWP_EMBEDDED_CONFIG__;
  (window as any).DEWPEmbeddedAnalytics = new EmbeddedAnalytics(config);
}

export default EmbeddedAnalytics;