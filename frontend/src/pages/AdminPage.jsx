import { useState } from 'react'
import { useAdminUsers, useAdminAnalytics, useAuditLogs } from '../hooks/useApi'
import { formatCurrency, formatDate } from '../utils/format'

export default function AdminPage() {
  const [usersPage, setUsersPage] = useState(0)
  const [logsPage, setLogsPage] = useState(0)
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7))
  const pageSize = 20

  const { data: users, isLoading: usersLoading } = useAdminUsers({ skip: usersPage * pageSize, limit: pageSize })
  const { data: analytics } = useAdminAnalytics(month)
  const { data: logs } = useAuditLogs({ skip: logsPage * pageSize, limit: pageSize })

  return (
    <div className="space-y-8">
      <div className="reveal-on-scroll">
        <h1 className="display-text mb-2">Admin Dashboard</h1>
        <p className="subheading-text">System administration and monitoring</p>
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <AdminStatCard title="Total Users" value={analytics?.total_users || 0} icon="👥" color="text-blue-600" delay="0s" />
        <AdminStatCard title="Total Transactions" value={analytics?.total_transactions || 0} icon="💳" color="text-green-600" delay="0.1s" />
        <AdminStatCard title="Total Volume" value={formatCurrency(analytics?.total_volume)} icon="💰" color="text-purple-600" delay="0.2s" />
        <AdminStatCard title="Avg Budget Health" value={`${(analytics?.avg_budget_health || 0).toFixed(1)}%`} icon="📊" color="text-orange-600" delay="0.3s" />
      </div>

      {/* Users Management */}
      <div className="glass-card reveal-on-scroll" style={{ animationDelay: '0.2s' }}>
        <div className="card-header flex items-center justify-between">
          <h3 className="heading-text">User Management</h3>
          <select
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="clay-select w-auto"
          >
            {Array.from({ length: 12 }, (_, i) => {
              const date = new Date()
              date.setMonth(date.getMonth() - i)
              const value = date.toISOString().slice(0, 7)
              return <option key={value} value={value}>{date.toLocaleString('default', { month: 'long', year: 'numeric' })}</option>
            })}
          </select>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm font-medium text-ink-500 border-b border-ink-100">
                  <th className="pb-4 px-4">User</th>
                  <th className="pb-4 px-4">Email</th>
                  <th className="pb-4 px-4">Role</th>
                  <th className="pb-4 px-4">Status</th>
                  <th className="pb-4 px-4">Monthly Income</th>
                  <th className="pb-4 px-4">Joined</th>
                  <th className="pb-4 px-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100">
                {usersLoading ? (
                  <tr><td colSpan={7} className="py-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent mx-auto" /></td></tr>
                ) : users?.map((user) => (
                  <tr key={user.id} className="hover:bg-white/30 transition-colors duration-300">
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-xs font-bold">
                          {user.full_name?.charAt(0) || 'U'}
                        </div>
                        <div>
                          <div className="font-medium text-ink-900">{user.full_name}</div>
                          <div className="text-xs text-ink-500">{user.id.slice(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-ink-600">{user.email}</td>
                    <td className="py-4 px-4">
                      <span className={`clay-badge ${user.role === 'ADMIN' ? 'clay-badge-warning' : user.role === 'SUPER_ADMIN' ? 'clay-badge-danger' : 'clay-badge-info'}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={user.is_active ? 'clay-badge-success' : 'clay-badge-danger'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-ink-900 font-medium">{formatCurrency(user.monthly_income)}</td>
                    <td className="py-4 px-4 text-ink-600">{user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2">
                        {user.is_active ? (
                          <button className="clay-badge-danger text-xs py-1.5 px-3" onClick={() => deactivateUser(user.id)}>Deactivate</button>
                        ) : (
                          <button className="clay-badge-success text-xs py-1.5 px-3" onClick={() => activateUser(user.id)}>Activate</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between pt-4">
            <p className="text-sm text-ink-600">Page {usersPage + 1}</p>
            <div className="flex space-x-2">
              <button
                onClick={() => setUsersPage(p => Math.max(0, p - 1))}
                disabled={usersPage === 0}
                className="clay-btn-secondary text-sm"
              >
                Previous
              </button>
              <button
                onClick={() => setUsersPage(p => p + 1)}
                disabled={!users || users.length < pageSize}
                className="clay-btn-secondary text-sm"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Logs */}
      <div className="glass-card reveal-on-scroll" style={{ animationDelay: '0.3s' }}>
        <div className="card-header">
          <h3 className="heading-text">Audit Logs</h3>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm font-medium text-ink-500 border-b border-ink-100">
                  <th className="pb-4 px-4">Time</th>
                  <th className="pb-4 px-4">User</th>
                  <th className="pb-4 px-4">Action</th>
                  <th className="pb-4 px-4">Entity</th>
                  <th className="pb-4 px-4">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100">
                {logs?.map((log, i) => (
                  <tr key={i} className="hover:bg-white/30 transition-colors duration-300">
                    <td className="py-3 px-4 text-sm text-ink-600">{formatDate(log.created_at, 'dd MMM yyyy, HH:mm:ss')}</td>
                    <td className="py-3 px-4 text-sm text-ink-900">{log.user_id?.slice(0, 8)}...</td>
                    <td className="py-3 px-4">
                      <span className="clay-badge-info">{log.action}</span>
                    </td>
                    <td className="py-3 px-4 text-sm text-ink-600">{log.entity_type} {log.entity_id?.slice(0, 8)}</td>
                    <td className="py-3 px-4 text-sm text-ink-500">{log.ip || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between pt-4">
            <p className="text-sm text-ink-600">Page {logsPage + 1}</p>
            <div className="flex space-x-2">
              <button onClick={() => setLogsPage(p => Math.max(0, p - 1))} disabled={logsPage === 0} className="clay-btn-secondary text-sm">Previous</button>
              <button onClick={() => setLogsPage(p => p + 1)} disabled={!logs || logs.length < pageSize} className="clay-btn-secondary text-sm">Next</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function AdminStatCard({ title, value, icon, color, delay }) {
  return (
    <div
      className="glass-card p-6 reveal-on-scroll"
      style={{ animationDelay: delay }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-ink-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-ink-900">{value}</p>
        </div>
        <div className={`text-3xl ${color}`}>{icon}</div>
      </div>
    </div>
  )
}

function deactivateUser(userId) {
  if (window.confirm('Deactivate this user?')) {
    console.log('Deactivate user:', userId)
  }
}

function activateUser(userId) {
  if (window.confirm('Activate this user?')) {
    console.log('Activate user:', userId)
  }
}