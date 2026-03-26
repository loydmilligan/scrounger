const API_BASE = '/api';

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  // Items
  getItems: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/items${query}`);
  },
  getItem: (id: number) => request<any>(`/items/${id}`),
  createItem: (data: any) => request<any>('/items', { method: 'POST', body: JSON.stringify(data) }),
  updateItem: (id: number, data: any) => request<any>(`/items/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteItem: (id: number) => request<any>(`/items/${id}`, { method: 'DELETE' }),

  // Leads
  getLeads: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/leads${query}`);
  },
  getLead: (id: number) => request<any>(`/leads/${id}`),
  createLead: (data: any) => request<any>('/leads', { method: 'POST', body: JSON.stringify(data) }),
  updateLead: (id: number, data: any) => request<any>(`/leads/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteLead: (id: number) => request<any>(`/leads/${id}`, { method: 'DELETE' }),
  importRedditLeads: (data: { url: string; item_id: number }) =>
    request<any>('/leads/import-reddit', { method: 'POST', body: JSON.stringify(data) }),

  // Sales
  getSales: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/sales${query}`);
  },
  getSalesStats: () => request<any>('/sales/stats'),
  createSale: (data: any) => request<any>('/sales', { method: 'POST', body: JSON.stringify(data) }),
  updateSale: (id: number, data: any) => request<any>(`/sales/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteSale: (id: number) => request<any>(`/sales/${id}`, { method: 'DELETE' }),

  // Settings
  getAISettings: () => request<any>('/settings/ai'),
  updateAISettings: (data: any) => request<any>('/settings/ai', { method: 'PUT', body: JSON.stringify(data) }),
  testAIConnection: () => request<any>('/settings/ai/test', { method: 'POST' }),
  getAIModels: () => request<any[]>('/settings/ai-models'),
  createAIModel: (data: any) => request<any>('/settings/ai-models', { method: 'POST', body: JSON.stringify(data) }),
  lookupModel: (modelId: string) => request<any>(`/settings/ai-models/lookup/${encodeURIComponent(modelId)}`),
  updateAIModel: (id: number, data: any) => request<any>(`/settings/ai-models/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteAIModel: (id: number) => request<any>(`/settings/ai-models/${id}`, { method: 'DELETE' }),
  toggleFavorite: (id: number) => request<any>(`/settings/ai-models/${id}/favorite`, { method: 'POST' }),

  // AI
  chat: (data: any) => request<any>('/ai/chat', { method: 'POST', body: JSON.stringify(data) }),
  generatePost: (data: any) => request<any>('/ai/generate-post', { method: 'POST', body: JSON.stringify(data) }),
  priceCheck: (data: any) => request<any>('/ai/price-check', { method: 'POST', body: JSON.stringify(data) }),
  shippingHelp: (data: any) => request<any>('/ai/shipping-help', { method: 'POST', body: JSON.stringify(data) }),
  parseBundle: (data: { url: string; create_items?: boolean }) =>
    request<any>('/ai/parse-bundle', { method: 'POST', body: JSON.stringify(data) }),

  // Webhooks (for displaying Reddit messages)
  getRedditMessages: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<any>(`/webhook/reddit-messages${query}`);
  },

  // Export
  exportItemsCSV: () => `${API_BASE}/export/items/csv`,
  exportLeadsCSV: () => `${API_BASE}/export/leads/csv`,
  exportSalesCSV: () => `${API_BASE}/export/sales/csv`,
  exportCalendar: () => `${API_BASE}/export/calendar/leads.ics`,
  exportTasks: () => `${API_BASE}/export/tasks/leads.ics`,
  getTemplate: () => `${API_BASE}/export/template/items.csv`,
};
