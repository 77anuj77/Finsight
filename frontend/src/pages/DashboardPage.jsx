import { useState, useEffect, useRef } from 'react'
import { useDashboard } from '../hooks/useApi'
import { formatCurrency, getMonthName } from '../utils/format'
import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts'
import { useAuth } from '../context/AuthContext'

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

export default function DashboardPage() {
  const { user } = useAuth()
  const [month, setMonth] = useState(new Date())
  const monthKey = getMonthName(month)

  const { data: dashboard, isLoading, error, refetch } = useDashboard(monthKey)

  // Mock data for charts when backend not ready
  const mockCategoryData = [
    { name: 'Food & Dining', value: 4500, color: '#22c55e' },
    { name: 'Transport', value: 2000, color: '#3b82f6' },
    { name: 'Shopping', value: 1500, color: '#f59e0b' },
    { name: 'Entertainment', value: 1000, color: '#ef4444' },
    { name: 'Other', value: 800, color: '#8b5cf6' },
  ]

  const mockTrendData = [
    { month: 'Apr', income: 15000, expense: 12000 },
    { month: 'May', income: 15000, expense: 13500 },
    { month: 'Jun', income: 15000, expense: 11000 },
    { month: 'Jul', income: 15000, expense: 14000 },
    { month: 'Aug', income: 15000, expense: 12500 },
    { month: 'Sep', income: 15000, expense: 13000 },
  ]

  const categoryData = dashboard?.category_breakdown?.map((c, i) => ({
    name: `Category ${c.category_id}`,
    value: c.amount,
    color: COLORS[i % COLORS.length],
  })) || mockCategoryData

  const trendData = dashboard?.monthly_trends || mockTrendData

  const handleMonthChange = (delta) => {
    const newMonth = new Date(month)
    newMonth.setMonth(newMonth.getMonth() + delta)
    setMonth(newMonth)
    refetch()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Dashboard</h1>
          <p className="subheading-text">Welcome back, {user?.full_name}</p>
        </div>
        <div className="flex items-center space-x-4 reveal-on-scroll" style={{ animationDelay: '0.1s' }}>
          <button
            onClick={() => handleMonthChange(-1)}
            className="clay-btn-secondary"
          >
            ← Previous
          </button>
          <span className="text-lg font-semibold text-ink-900 min-w-[200px] text-center">
            {monthKey}
          </span>
          <button
            onClick={() => handleMonthChange(1)}
            className="clay-btn-secondary"
            disabled={new Date(monthKey) > new Date()}
          >
            Next →
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Balance"
          value={formatCurrency(dashboard?.total_balance || 25000)}
          icon="💰"
          color="text-primary-600"
          delay="0s"
        />
        <KPICard
          title="Monthly Income"
          value={formatCurrency(dashboard?.total_income || 15000)}
          icon="📈"
          color="text-green-600"
          delay="0.1s"
        />
        <KPICard
          title="Total Expenses"
          value={formatCurrency(dashboard?.total_expense || 12000)}
          icon="💸"
          color="text-red-600"
          delay="0.2s"
        />
        <KPICard
          title="Savings Rate"
          value={`${(dashboard?.savings_rate || 20).toFixed(1)}%`}
          icon="🎯"
          color="text-blue-600"
          delay="0.3s"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.2s' }}>
          <h3 className="heading-text mb-6">Spending by Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  fill="#8884d8"
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {categoryData.map((entry, index) => (
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
                  formatter={(value) => formatCurrency(value)}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Trend */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.3s' }}>
          <h3 className="heading-text mb-6">Monthly Trend (6 months)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} tickFormatter={formatCurrency} />
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
      </div>

      {/* Budget Alerts & Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Budget Alerts */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.4s' }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="heading-text">Budget Alerts</h3>
            <span className="clay-badge-warning">{dashboard?.budget_alerts_count || 2} alerts</span>
          </div>
          <div className="space-y-4">
            <BudgetAlert
              category="Food & Dining"
              spent={4500}
              limit={4000}
              percentage={112}
            />
            <BudgetAlert
              category="Transport"
              spent={1800}
              limit={2000}
              percentage={90}
            />
            <BudgetAlert
              category="Shopping"
              spent={500}
              limit={2000}
              percentage={25}
            />
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="glass-card p-6 reveal-on-scroll" style={{ animationDelay: '0.5s' }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="heading-text">Recent Transactions</h3>
            <a
              href="/transactions"
              className="text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors duration-300"
            >
              View all
            </a>
          </div>
          <div className="space-y-3">
            {dashboard?.recent_transactions?.slice(0, 5).map((txn, i) => (
              <TransactionRow key={i} txn={txn} />
            )) || [
              { payee: 'Zomato', amount: -350, type: 'EXPENSE', date: '2 hours ago' },
              { payee: 'Uber', amount: -120, type: 'EXPENSE', date: '5 hours ago' },
              { payee: 'Monthly Allowance', amount: 12000, type: 'INCOME', date: '2 days ago' },
              { payee: 'Netflix', amount: -649, type: 'EXPENSE', date: '3 days ago' },
              { payee: 'Swiggy', amount: -280, type: 'EXPENSE', date: '4 days ago' },
            ].map((txn, i) => (
              <TransactionRow key={i} txn={txn} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function KPICard({ title, value, icon, color, delay }) {
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

function BudgetAlert({ category, spent, limit, percentage }) {
  const isOver = percentage > 100
  const isWarning = percentage > 80 && !isOver

  return (
    <div className="p-4 rounded-squircle bg-white/50 border border-white/60">
      <div className="flex items-center justify-between mb-3">
        <span className="font-medium text-ink-900">{category}</span>
        <span className={`text-sm font-semibold ${isOver ? 'text-red-600' : isWarning ? 'text-yellow-600' : 'text-green-600'}`}>
          {percentage}%
        </span>
      </div>
      <div className="h-2.5 bg-ink-100 rounded-pill overflow-hidden">
        <div
          className={`h-full transition-all duration-700 ease-fluid ${isOver ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      <p className="text-xs text-ink-500 mt-2 text-right">
        {formatCurrency(spent)} / {formatCurrency(limit)}
      </p>
    </div>
  )
}

function TransactionRow({ txn }) {
  const isIncome = txn.type === 'INCOME' || txn.amount > 0
  return (
    <div className="flex items-center justify-between py-3 border-b border-ink-100 last:border-0">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-ink-100 to-ink-200 flex items-center justify-center text-sm shadow-clay-sm">
          {isIncome ? '📈' : '💸'}
        </div>
        <div>
          <p className="text-sm font-medium text-ink-900">{txn.payee}</p>
          <p className="text-xs text-ink-500">{txn.date}</p>
        </div>
      </div>
      <span className={`font-semibold ${isIncome ? 'text-green-600' : 'text-red-600'}`}>
        {isIncome ? '+' : ''}{formatCurrency(txn.amount)}
      </span>
    </div>
  )
}