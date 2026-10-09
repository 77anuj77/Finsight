/**
 * API Endpoints
 * Centralized endpoint definitions for the frontend
 */

export const ENDPOINTS = {
  // Auth
  auth: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    refresh: '/api/auth/refresh',
    logout: '/api/auth/logout',
    me: '/api/auth/me',
  },

  // Accounts
  accounts: {
    list: '/api/accounts',
    create: '/api/accounts',
    get: (id) => `/api/accounts/${id}`,
    update: (id) => `/api/accounts/${id}`,
    delete: (id) => `/api/accounts/${id}`,
  },

  // Transactions
  transactions: {
    list: '/api/transactions',
    create: '/api/transactions',
    get: (id) => `/api/transactions/${id}`,
    update: (id) => `/api/transactions/${id}`,
    delete: (id) => `/api/transactions/${id}`,
    confirm: (id) => `/api/transactions/${id}/confirm`,
  },

  // Budgets
  budgets: {
    list: '/api/budgets',
    create: '/api/budgets',
    get: (id) => `/api/budgets/${id}`,
    update: (id) => `/api/budgets/${id}`,
    delete: (id) => `/api/budgets/${id}`,
    utilization: (id) => `/api/budgets/${id}/utilization`,
  },

  // Goals
  goals: {
    list: '/api/goals',
    create: '/api/goals',
    get: (id) => `/api/goals/${id}`,
    update: (id) => `/api/goals/${id}`,
    delete: (id) => `/api/goals/${id}`,
    progress: (id) => `/api/goals/${id}/progress`,
    sweep: (id) => `/api/goals/${id}/sweep`,
  },

  // Analytics
  analytics: {
    dashboard: '/api/analytics/dashboard',
    trends: '/api/analytics/trends',
    categoryBreakdown: '/api/analytics/category-breakdown',
    topPayees: '/api/analytics/top-payees',
    budgetVsActual: '/api/analytics/budget-vs-actual',
    netWorth: '/api/analytics/net-worth',
  },

  // Insights
  insights: {
    latest: '/api/insights/latest',
    generate: '/api/insights/generate',
    history: '/api/insights/history',
  },

  // Reports
  reports: {
    monthly: '/api/reports/monthly',
    yearly: '/api/reports/yearly',
    exportTransactions: '/api/reports/transactions/export',
  },

  // Admin
  admin: {
    users: '/api/admin/users',
    user: (id) => `/api/admin/users/${id}`,
    deactivateUser: (id) => `/api/admin/users/${id}/deactivate`,
    activateUser: (id) => `/api/admin/users/${id}/activate`,
    analytics: '/api/admin/analytics/aggregate',
    auditLogs: '/api/admin/audit-logs',
  },
}

// Helper to build query strings
export function buildQuery(params) {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value)
    }
  })
  return searchParams.toString()
}