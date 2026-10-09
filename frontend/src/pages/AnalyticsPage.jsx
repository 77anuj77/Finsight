import { useState } from 'react'
import { useDashboard, useTrends, useCategoryBreakdown, useTopPayees, useBudgetVsActual, useNetWorth } from '../hooks/useApi'
import { formatCurrency, getMonthName } from '../utils/format'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts'

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

export default function AnalyticsPage() {
  const [month, setMonth] = useState(new Date())
  const monthKey = getMonthName(month)

  const { data: dashboard } = useDashboard(monthKey)
  const { data: trends } = useTrends(6)
  const { data: categoryBreakdown } = useCategoryBreakdown(monthKey)
  const { data: topPayees } = useTopPayees(monthKey, 10)
  const { data: budgetVsActual } = useBudgetVsActual(monthKey)
  const { data: netWorth } = useNetWorth()

  const handleMonthChange = (delta) => {
    const newMonth = new Date(month)
    newMonth.setMonth(newMonth.getMonth() + delta)
    setMonth(newMonth)
  }

  const catData = categoryBreakdown?.map((c, i) => ({
    name: `Cat ${c.category_id}`,
    value: c.amount,
    color: COLORS[i % COLORS.length],
    percentage: c.percentage,
  })) || []

  const trendData = trends || []

  const budgetData = budgetVsActual?.map((b, i) => ({
    name: `Cat ${b.category_id}`,
    budget: b.limit_amount,
    actual: b.spent_amount,
    color: COLORS[i % COLORS.length],
  })) || []

  const payeeData = topPayees || []

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Analytics</h1>
          <p className="subheading-text">Deep dive into your spending patterns</p>
        </div>
        <div className="flex items-center space-x-4 reveal-on-scroll" style={{ animationDelay: '0.1s' }}>
          <button onClick={() => handleMonthChange(-1)} className="clay-btn-secondary">← Previous</button>
          <span className="text-lg font-semibold text-ink-900 min-w-[200px] text-center">{monthKey}</span>
          <button onClick={() => handleMonthChange(1)} className="clay-btn-secondary" disabled={new Date(monthKey) > new Date()}>Next →</button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Income" value={formatCurrency(dashboard?.total_income)} icon="📈" color="text-green-600" delay="0s" />
        <StatCard title="Total Expenses" value={formatCurrency(dashboard?.total_expense)} icon="💸" color="text-red-600" delay="0.1s" />
        <StatCard title="Net Savings" value={formatCurrency(dashboard?.net_savings)} icon="💰" color="text-blue-600" delay="0.2s" />
        <StatCard title="Savings Rate" value={`${(dashboard?.savings_rate || 0).toFixed(1)}%`} icon="🎯" color="text-purple-600" delay="0.3s" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown Pie */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.2s' }}>
          <h3 className="heading-text mb-6">Spending by Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={catData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {catData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: '1rem',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
                  }}
                  formatter={(value) => [formatCurrency(value), 'Amount']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Payees Bar */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.3s' }}>
          <h3 className="heading-text mb-6">Top Payees</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={payeeData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis type="number" stroke="#64748b" tickFormatter={formatCurrency} />
                <YAxis type="category" dataKey="payee" width={120} stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: '1rem',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
                  }}
                  formatter={(value) => [formatCurrency(value), 'Amount']}
                />
                <Bar dataKey="amount" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trend */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.4s' }}>
          <h3 className="heading-text mb-6">Monthly Income vs Expenses</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis dataKey="month" stroke="#64748b" />
                <YAxis stroke="#64748b" tickFormatter={formatCurrency} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: '1rem',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
                  }}
                  formatter={(value, name) => [
                    name === 'income' ? 'Income' : 'Expense',
                    formatCurrency(value)
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="income"
                  stroke="#22c55e"
                  strokeWidth={2.5}
                  dot={{ fill: '#22c55e', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Income"
                />
                <Line
                  type="monotone"
                  dataKey="expense"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Expense"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Budget vs Actual */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.5s' }}>
          <h3 className="heading-text mb-6">Budget vs Actual</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={budgetData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis type="number" stroke="#64748b" tickFormatter={formatCurrency} />
                <YAxis type="category" dataKey="name" width={100} stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: '1rem',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
                  }}
                  formatter={(value) => [formatCurrency(value), 'Amount']}
                />
                <Bar dataKey="budget" fill="#3b82f6" name="Budget" radius={[0, 4, 4, 0]} />
                <Bar dataKey="actual" fill="#ef4444" name="Actual" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Net Worth */}
      <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.6s' }}>
        <h3 className="heading-text mb-6">Net Worth Breakdown</h3>
        <div className="space-y-3">
          {netWorth?.accounts?.map((acc, i) => (
            <div key={acc.id} className="flex items-center justify-between p-4 bg-white/30 rounded-squircle border border-white/40">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-primary-600 font-bold">
                  {acc.type[0]}
                </div>
                <div>
                  <p className="font-medium text-ink-900">{acc.name}</p>
                  <p className="text-sm text-ink-500">{acc.type}</p>
                </div>
              </div>
              <span className="font-semibold text-ink-900">{formatCurrency(acc.balance)}</span>
            </div>
          ))}
          <div className="border-t border-ink-100 pt-4 flex justify-between items-center">
            <span className="font-bold text-ink-900 text-lg">Total Net Worth</span>
            <span className="font-bold text-2xl text-primary-600">{formatCurrency(netWorth?.total_net_worth)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color, delay }) {
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