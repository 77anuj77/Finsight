import { useState } from 'react'
import { useGoals, useCreateGoal, useUpdateGoal, useDeleteGoal, useGoalProgress, useTriggerSweep } from '../hooks/useApi'
import { formatCurrency, formatDate, formatPercentage } from '../utils/format'

export default function GoalsPage() {
  const [showModal, setShowModal] = useState(false)
  const [editingGoal, setEditingGoal] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    target_amount: '',
    auto_sweep_pct: 0,
    deadline: '',
  })

  const { data: goals, isLoading, refetch } = useGoals()
  const createGoal = useCreateGoal()
  const updateGoal = useUpdateGoal()
  const deleteGoal = useDeleteGoal()
  const triggerSweep = useTriggerSweep()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingGoal) {
        await updateGoal.mutateAsync({ id: editingGoal.id, data: formData })
      } else {
        await createGoal.mutateAsync(formData)
      }
      setShowModal(false)
      resetForm()
      refetch()
    } catch (err) {
      console.error('Error saving goal:', err)
    }
  }

  const handleEdit = (goal) => {
    setEditingGoal(goal)
    setFormData({
      name: goal.name,
      target_amount: goal.target_amount,
      auto_sweep_pct: goal.auto_sweep_pct,
      deadline: goal.deadline || '',
    })
    setShowModal(true)
  }

  const handleDelete = async (goal) => {
    if (window.confirm(`Delete goal "${goal.name}"?`)) {
      try {
        await deleteGoal.mutateAsync(goal.id)
        refetch()
      } catch (err) {
        console.error('Error deleting goal:', err)
      }
    }
  }

  const handleSweep = async (goal) => {
    try {
      await triggerSweep.mutateAsync(goal.id)
      refetch()
    } catch (err) {
      console.error('Error triggering sweep:', err)
    }
  }

  const handleNew = () => {
    setEditingGoal(null)
    resetForm()
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({ name: '', target_amount: '', auto_sweep_pct: 0, deadline: '' })
    setEditingGoal(null)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div></div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Savings Goals</h1>
          <p className="subheading-text">Track your financial goals and progress</p>
        </div>
        <button
          onClick={handleNew}
          className="clay-btn-primary reveal-on-scroll"
          style={{ animationDelay: '0.1s' }}
        >
          Add Goal
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals?.map((goal, i) => (
          <GoalCard
            key={goal.id}
            goal={goal}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onSweep={handleSweep}
            delay={`0.${i * 1}s`}
          />
        ))}
      </div>

      {(!goals || goals.length === 0) && (
        <div className="glass-card p-12 text-center reveal-on-scroll">
          <p className="text-ink-500 mb-4">No savings goals yet</p>
          <button onClick={handleNew} className="clay-btn-primary">Create your first goal</button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <Modal
          title={editingGoal ? 'Edit Goal' : 'Add Savings Goal'}
          onClose={() => setShowModal(false)}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Goal Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="clay-input"
                required
                placeholder="e.g., Emergency Fund"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Target Amount</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.target_amount}
                onChange={(e) => setFormData({...formData, target_amount: e.target.value})}
                className="clay-input"
                required
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Auto-sweep Percentage</label>
              <input
                type="number"
                step="1"
                min="0"
                max="100"
                value={formData.auto_sweep_pct}
                onChange={(e) => setFormData({...formData, auto_sweep_pct: parseInt(e.target.value) || 0})}
                className="clay-input"
                placeholder="0"
              />
              <p className="text-xs text-ink-500 mt-1">Percentage of monthly income to auto-save</p>
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Deadline (Optional)</label>
              <input
                type="date"
                value={formData.deadline}
                onChange={(e) => setFormData({...formData, deadline: e.target.value})}
                className="clay-input"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={() => setShowModal(false)} className="clay-btn-secondary">Cancel</button>
              <button type="submit" disabled={createGoal.isPending || updateGoal.isPending} className="clay-btn-primary">
                {editingGoal ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

function GoalCard({ goal, onEdit, onDelete, onSweep, delay }) {
  const { data: progress, isLoading } = useGoalProgress(goal.id)

  const percentage = progress?.progress_percentage || 0
  const isAchieved = goal.status === 'ACHIEVED'

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
        <h3 className="font-semibold text-ink-900">{goal.name}</h3>
        <span className={`clay-badge ${isAchieved ? 'clay-badge-success' : goal.status === 'PAUSED' ? 'clay-badge-warning' : 'clay-badge-info'}`}>
          {goal.status}
        </span>
      </div>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-ink-500">Progress</span>
            <span className="font-medium text-ink-900">{percentage.toFixed(1)}%</span>
          </div>
          <div className="h-3 bg-ink-100 rounded-pill overflow-hidden">
            <div
              className={`h-full transition-all duration-700 ease-fluid ${isAchieved ? 'bg-green-500' : 'bg-primary-500'}`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-ink-500">Target</p>
            <p className="font-medium text-ink-900">{formatCurrency(goal.target_amount)}</p>
          </div>
          <div>
            <p className="text-ink-500">Saved</p>
            <p className="font-medium text-primary-600">{formatCurrency(goal.current_amount)}</p>
          </div>
          <div>
            <p className="text-ink-500">Remaining</p>
            <p className="font-medium text-ink-900">{formatCurrency(goal.target_amount - goal.current_amount)}</p>
          </div>
          <div>
            <p className="text-ink-500">Auto-sweep</p>
            <p className="font-medium text-ink-900">{goal.auto_sweep_pct}%</p>
          </div>
        </div>
        {goal.deadline && (
          <p className="text-xs text-ink-500">
            Deadline: {formatDate(goal.deadline)}
          </p>
        )}
      </div>
      <div className="flex justify-end space-x-2 mt-4 pt-4 border-t border-ink-100 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        {!isAchieved && (
          <button
            onClick={() => onSweep(goal)}
            className="clay-badge-info text-xs py-1.5 px-3"
            disabled={triggerSweep.isPending}
          >
            Trigger Sweep
          </button>
        )}
        <button onClick={() => onEdit(goal)} className="clay-badge-info text-xs py-1.5 px-3">Edit</button>
        <button onClick={() => onDelete(goal)} className="clay-badge-danger text-xs py-1.5 px-3">Delete</button>
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