import { useState } from 'react'
import { useBudgets, useCreateBudget, useUpdateBudget, useDeleteBudget, useBudgetUtilization } from '../hooks/useApi'
import { formatCurrency, getMonthName } from '../utils/format'

export default function BudgetsPage() {
  const [showModal, setShowModal] = useState(false)
  const [editingBudget, setEditingBudget] = useState(null)
  const [month, setMonth] = useState(new Date())
  const [formData, setFormData] = useState({
    category_id: 2,
    limit_amount: '',
  })

  const monthKey = getMonthName(month)
  const { data: budgets, isLoading, refetch } = useBudgets(monthKey)
  const createBudget = useCreateBudget()
  const updateBudget = useUpdateBudget()
  const deleteBudget = useDeleteBudget()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingBudget) {
        await updateBudget.mutateAsync({ id: editingBudget.id, data: formData })
      } else {
        await createBudget.mutateAsync({ ...formData, month: monthKey })
      }
      setShowModal(false)
      resetForm()
      refetch()
    } catch (err) {
      console.error('Error saving budget:', err)
    }
  }

  const handleEdit = (budget) => {
    setEditingBudget(budget)
    setFormData({ category_id: budget.category_id, limit_amount: budget.limit_amount })
    setShowModal(true)
  }

  const handleDelete = async (budget) => {
    if (window.confirm(`Delete budget for category ${budget.category_id}?`)) {
      try {
        await deleteBudget.mutateAsync(budget.id)
        refetch()
      } catch (err) {
        console.error('Error deleting budget:', err)
      }
    }
  }

  const handleNew = () => {
    setEditingBudget(null)
    resetForm()
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({ category_id: 2, limit_amount: '' })
    setEditingBudget(null)
  }

  const handleMonthChange = (delta) => {
    const newMonth = new Date(month)
    newMonth.setMonth(newMonth.getMonth() + delta)
    setMonth(newMonth)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div></div>
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Budgets</h1>
          <p className="subheading-text">Set and track your spending limits</p>
        </div>
        <div className="flex items-center space-x-4 reveal-on-scroll" style={{ animationDelay: '0.1s' }}>
          <button onClick={() => handleMonthChange(-1)} className="clay-btn-secondary">← Previous</button>
          <span className="text-lg font-semibold text-ink-900 min-w-[200px] text-center">{monthKey}</span>
          <button onClick={() => handleMonthChange(1)} className="clay-btn-secondary" disabled={new Date(monthKey) > new Date()}>Next →</button>
          <button onClick={handleNew} className="clay-btn-primary ml-4">Add Budget</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets?.map((budget, i) => (
          <BudgetCard
            key={budget.id}
            budget={budget}
            onEdit={handleEdit}
            onDelete={handleDelete}
            delay={`0.${i * 1}s`}
          />
        ))}
      </div>

      {(!budgets || budgets.length === 0) && (
        <div className="glass-card p-12 text-center reveal-on-scroll">
          <p className="text-ink-500 mb-4">No budgets set for {monthKey}</p>
          <button onClick={handleNew} className="clay-btn-primary">Create your first budget</button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <Modal
          title={editingBudget ? 'Edit Budget' : 'Add Budget'}
          onClose={() => setShowModal(false)}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Category</label>
              <select
                value={formData.category_id}
                onChange={(e) => setFormData({...formData, category_id: parseInt(e.target.value)})}
                className="clay-select"
                required
              >
                <option value={2}>Food & Dining</option>
                <option value={3}>Transport</option>
                <option value={4}>Rent</option>
                <option value={5}>Education</option>
                <option value={6}>Subscriptions</option>
                <option value={7}>Shopping</option>
                <option value={8}>Entertainment</option>
                <option value={9}>Health</option>
                <option value={10}>Savings</option>
                <option value={11}>Other</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Limit Amount</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.limit_amount}
                onChange={(e) => setFormData({...formData, limit_amount: e.target.value})}
                className="clay-input"
                required
                placeholder="0.00"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={() => setShowModal(false)} className="clay-btn-secondary">Cancel</button>
              <button type="submit" disabled={createBudget.isPending || updateBudget.isPending} className="clay-btn-primary">
                {editingBudget ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

function BudgetCard({ budget, onEdit, onDelete, delay }) {
  const { data: utilization, isLoading } = useBudgetUtilization(budget.id)

  const percentage = utilization?.utilization_percentage || 0
  const isOver = utilization?.is_over_budget || false
  const isWarning = percentage > 80 && !isOver

  if (isLoading) {
    return (
      <div className="glass-card animate-pulse">
        <div className="p-6 h-48"></div>
      </div>
    )
  }

  return (
    <div
      className="glass-card p-6 reveal-on-scroll group"
      style={{ animationDelay: delay }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-ink-900">Category {budget.category_id}</h3>
        <span className={`clay-badge ${isOver ? 'clay-badge-danger' : isWarning ? 'clay-badge-warning' : 'clay-badge-success'}`}>
          {isOver ? 'Over Budget' : isWarning ? 'Warning' : 'On Track'}
        </span>
      </div>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-ink-500">Spent</span>
            <span className="font-medium text-ink-900">{formatCurrency(utilization?.spent_amount || 0)}</span>
          </div>
          <div className="h-3 bg-ink-100 rounded-pill overflow-hidden">
            <div
              className={`h-full transition-all duration-700 ease-fluid ${isOver ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-green-500'}`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div>
            <p className="text-ink-500">Limit</p>
            <p className="font-medium text-ink-900">{formatCurrency(utilization?.limit_amount || budget.limit_amount)}</p>
          </div>
          <div>
            <p className="text-ink-500">Remaining</p>
            <p className={`font-medium ${isOver ? 'text-red-600' : 'text-green-600'}`}>
              {formatCurrency(utilization?.remaining_amount || budget.limit_amount)}
            </p>
          </div>
          <div>
            <p className="text-ink-500">Utilization</p>
            <p className="font-medium text-ink-900">{percentage.toFixed(1)}%</p>
          </div>
        </div>
        {utilization?.will_breach && (
          <div className="p-3 bg-yellow-50/80 border border-yellow-200/50 rounded-squircle text-yellow-800 text-sm">
            ⚠️ Projected to exceed budget by end of month
          </div>
        )}
      </div>
      <div className="flex justify-end space-x-2 mt-4 pt-4 border-t border-ink-100 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button onClick={() => onEdit(budget)} className="clay-badge-info text-xs py-1.5 px-3">Edit</button>
        <button onClick={() => onDelete(budget)} className="clay-badge-danger text-xs py-1.5 px-3">Delete</button>
      </div>
    </div>
  )
}

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 glass-overlay animate-fade-in"
        onClick={onClose}
        aria-hidden="true"
      />
      <div className="relative w-full max-w-md glass-modal p-8 animate-scale-in">
        <h2 className="text-xl font-bold text-ink-900 mb-6">{title}</h2>
        {children}
      </div>
    </div>
  )
}