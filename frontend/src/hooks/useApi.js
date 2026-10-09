import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import { ENDPOINTS, buildQuery } from '../api/endpoints'

// Query keys for consistent caching
export const QUERY_KEYS = {
  user: (id) => ['user', id],
  accounts: () => ['accounts'],
  account: (id) => ['account', id],
  transactions: (filters) => ['transactions', filters],
  transaction: (id) => ['transaction', id],
  budgets: (month) => ['budgets', month],
  budget: (id) => ['budget', id],
  budgetUtilization: (id) => ['budget', id, 'utilization'],
  goals: (status) => ['goals', status],
  goal: (id) => ['goal', id],
  goalProgress: (id) => ['goal', id, 'progress'],
  dashboard: (month) => ['dashboard', month],
  trends: (months) => ['trends', months],
  categoryBreakdown: (month) => ['categoryBreakdown', month],
  topPayees: (month) => ['topPayees', month],
  netWorth: () => ['netWorth'],
  insights: (month) => ['insights', month],
  insightsHistory: () => ['insights', 'history'],
  adminUsers: (params) => ['admin', 'users', params],
  adminAnalytics: (month) => ['admin', 'analytics', month],
  auditLogs: (params) => ['admin', 'auditLogs', params],
}

// Auth
export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ email, password }) => api.post(ENDPOINTS.auth.login, { email, password }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })
}

export function useRegister() {
  return useMutation({
    mutationFn: ({ email, password, full_name }) => api.post(ENDPOINTS.auth.register, { email, password, full_name }),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api.post(ENDPOINTS.auth.logout),
    onSuccess: () => {
      queryClient.clear()
    },
  })
}

// Accounts
export function useAccounts() {
  return useQuery({
    queryKey: QUERY_KEYS.accounts(),
    queryFn: () => api.get(ENDPOINTS.accounts.list).then(res => res.data),
  })
}

export function useAccount(id) {
  return useQuery({
    queryKey: QUERY_KEYS.account(id),
    queryFn: () => api.get(ENDPOINTS.accounts.get(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useCreateAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post(ENDPOINTS.accounts.create, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.accounts() })
    },
  })
}

export function useUpdateAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => api.put(ENDPOINTS.accounts.update(id), data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.accounts() })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.account(id) })
    },
  })
}

export function useDeleteAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => api.delete(ENDPOINTS.accounts.delete(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.accounts() })
    },
  })
}

// Transactions
export function useTransactions(filters = {}) {
  const queryString = buildQuery(filters)
  return useQuery({
    queryKey: QUERY_KEYS.transactions(filters),
    queryFn: () => api.get(`${ENDPOINTS.transactions.list}?${queryString}`).then(res => res.data),
  })
}

export function useTransaction(id) {
  return useQuery({
    queryKey: QUERY_KEYS.transaction(id),
    queryFn: () => api.get(ENDPOINTS.transactions.get(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post(ENDPOINTS.transactions.create, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
  })
}

export function useUpdateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => api.put(ENDPOINTS.transactions.update(id), data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.transaction(id) })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => api.delete(ENDPOINTS.transactions.delete(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useConfirmTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, decision }) => api.post(ENDPOINTS.transactions.confirm(id), { decision }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.transaction(id) })
    },
  })
}

// Budgets
export function useBudgets(month) {
  return useQuery({
    queryKey: QUERY_KEYS.budgets(month),
    queryFn: () => api.get(`${ENDPOINTS.budgets.list}?month=${month}`).then(res => res.data),
  })
}

export function useBudget(id) {
  return useQuery({
    queryKey: QUERY_KEYS.budget(id),
    queryFn: () => api.get(ENDPOINTS.budgets.get(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useBudgetUtilization(id) {
  return useQuery({
    queryKey: QUERY_KEYS.budgetUtilization(id),
    queryFn: () => api.get(ENDPOINTS.budgets.utilization(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useCreateBudget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post(ENDPOINTS.budgets.create, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
    },
  })
}

export function useUpdateBudget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => api.put(ENDPOINTS.budgets.update(id), data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.budget(id) })
    },
  })
}

export function useDeleteBudget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => api.delete(ENDPOINTS.budgets.delete(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] })
    },
  })
}

// Goals
export function useGoals(status) {
  return useQuery({
    queryKey: QUERY_KEYS.goals(status),
    queryFn: () => api.get(`${ENDPOINTS.goals.list}${status ? `?status=${status}` : ''}`).then(res => res.data),
  })
}

export function useGoal(id) {
  return useQuery({
    queryKey: QUERY_KEYS.goal(id),
    queryFn: () => api.get(ENDPOINTS.goals.get(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useGoalProgress(id) {
  return useQuery({
    queryKey: QUERY_KEYS.goalProgress(id),
    queryFn: () => api.get(ENDPOINTS.goals.progress(id)).then(res => res.data),
    enabled: !!id,
  })
}

export function useCreateGoal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => api.post(ENDPOINTS.goals.create, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
}

export function useUpdateGoal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => api.put(ENDPOINTS.goals.update(id), data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.goal(id) })
    },
  })
}

export function useDeleteGoal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => api.delete(ENDPOINTS.goals.delete(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
}

export function useTriggerSweep() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => api.post(ENDPOINTS.goals.sweep(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

// Analytics
export function useDashboard(month) {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard(month),
    queryFn: () => api.get(`${ENDPOINTS.analytics.dashboard}?month=${month}`).then(res => res.data),
  })
}

export function useTrends(months = 6) {
  return useQuery({
    queryKey: QUERY_KEYS.trends(months),
    queryFn: () => api.get(`${ENDPOINTS.analytics.trends}?months=${months}`).then(res => res.data),
  })
}

export function useCategoryBreakdown(month) {
  return useQuery({
    queryKey: QUERY_KEYS.categoryBreakdown(month),
    queryFn: () => api.get(`${ENDPOINTS.analytics.categoryBreakdown}?month=${month}`).then(res => res.data),
  })
}

export function useTopPayees(month, limit = 10) {
  return useQuery({
    queryKey: QUERY_KEYS.topPayees(month),
    queryFn: () => api.get(`${ENDPOINTS.analytics.topPayees}?month=${month}&limit=${limit}`).then(res => res.data),
  })
}

export function useBudgetVsActual(month) {
  return useQuery({
    queryKey: ['budgetVsActual', month],
    queryFn: () => api.get(`${ENDPOINTS.analytics.budgetVsActual}?month=${month}`).then(res => res.data),
  })
}

export function useNetWorth() {
  return useQuery({
    queryKey: QUERY_KEYS.netWorth(),
    queryFn: () => api.get(ENDPOINTS.analytics.netWorth).then(res => res.data),
  })
}

// Insights
export function useLatestInsight(month) {
  return useQuery({
    queryKey: QUERY_KEYS.insights(month),
    queryFn: () => api.get(`${ENDPOINTS.insights.latest}?month=${month}`).then(res => res.data),
  })
}

export function useGenerateInsight() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (month) => api.post(`${ENDPOINTS.insights.generate}?month=${month}`),
    onSuccess: (_, month) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.insights(month) })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.insightsHistory() })
    },
  })
}

export function useInsightsHistory(limit = 12) {
  return useQuery({
    queryKey: QUERY_KEYS.insightsHistory(),
    queryFn: () => api.get(`${ENDPOINTS.insights.history}?limit=${limit}`).then(res => res.data),
  })
}

// Reports
export function useMonthlyReport(month, format = 'json') {
  return useQuery({
    queryKey: ['reports', 'monthly', month, format],
    queryFn: () => api.get(`${ENDPOINTS.reports.monthly}?month=${month}&format=${format}`).then(res => res.data),
  })
}

export function useExportTransactions(params) {
  const queryString = buildQuery(params)
  return useQuery({
    queryKey: ['reports', 'export', params],
    queryFn: () => api.get(`${ENDPOINTS.reports.exportTransactions}?${queryString}`).then(res => res.data),
    enabled: false, // Trigger manually
  })
}

// Admin
export function useAdminUsers(params = {}) {
  const queryString = buildQuery(params)
  return useQuery({
    queryKey: QUERY_KEYS.adminUsers(params),
    queryFn: () => api.get(`${ENDPOINTS.admin.users}?${queryString}`).then(res => res.data),
  })
}

export function useAdminAnalytics(month) {
  return useQuery({
    queryKey: QUERY_KEYS.adminAnalytics(month),
    queryFn: () => api.get(`${ENDPOINTS.admin.analytics}?month=${month}`).then(res => res.data),
  })
}

export function useAuditLogs(params = {}) {
  const queryString = buildQuery(params)
  return useQuery({
    queryKey: QUERY_KEYS.auditLogs(params),
    queryFn: () => api.get(`${ENDPOINTS.admin.auditLogs}?${queryString}`).then(res => res.data),
  })
}