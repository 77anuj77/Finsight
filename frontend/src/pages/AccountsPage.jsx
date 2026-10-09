import { useState } from 'react'
import { useAccounts, useCreateAccount, useUpdateAccount, useDeleteAccount } from '../hooks/useApi'
import { formatCurrency } from '../utils/format'

export default function AccountsPage() {
  const [showModal, setShowModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState(null)
  const [formData, setFormData] = useState({ name: '', type: 'BANK', currency: 'INR' })

  const { data: accounts, isLoading, refetch } = useAccounts()
  const createAccount = useCreateAccount()
  const updateAccount = useUpdateAccount()
  const deleteAccount = useDeleteAccount()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingAccount) {
        await updateAccount.mutateAsync({ id: editingAccount.id, data: formData })
      } else {
        await createAccount.mutateAsync(formData)
      }
      setShowModal(false)
      resetForm()
      refetch()
    } catch (err) {
      console.error('Error saving account:', err)
    }
  }

  const handleEdit = (account) => {
    setEditingAccount(account)
    setFormData({ name: account.name, type: account.type, currency: account.currency })
    setShowModal(true)
  }

  const handleDelete = async (account) => {
    if (window.confirm(`Delete ${account.name}? This cannot be undone.`)) {
      try {
        await deleteAccount.mutateAsync(account.id)
        refetch()
      } catch (err) {
        console.error('Error deleting account:', err)
      }
    }
  }

  const handleNew = () => {
    setEditingAccount(null)
    resetForm()
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({ name: '', type: 'BANK', currency: 'INR' })
    setEditingAccount(null)
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div></div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Accounts</h1>
          <p className="subheading-text">Manage your financial accounts</p>
        </div>
        <button
          onClick={handleNew}
          className="clay-btn-primary reveal-on-scroll"
          style={{ animationDelay: '0.1s' }}
        >
          Add Account
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts?.map((account, i) => (
          <AccountCard
            key={account.id}
            account={account}
            onEdit={handleEdit}
            onDelete={handleDelete}
            delay={`0.${i * 1}s`}
          />
        ))}
      </div>

      {(!accounts || accounts.length === 0) && (
        <div className="glass-card p-12 text-center reveal-on-scroll">
          <p className="text-ink-500 mb-4">No accounts yet. Click "Add Account" to get started.</p>
          <button onClick={handleNew} className="clay-btn-primary">Create your first account</button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <Modal
          title={editingAccount ? 'Edit Account' : 'Add Account'}
          onClose={() => setShowModal(false)}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Account Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="clay-input"
                required
                placeholder="e.g., Main Bank Account"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Account Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({...formData, type: e.target.value})}
                className="clay-select"
                required
              >
                <option value="BANK">Bank Account</option>
                <option value="CASH">Cash</option>
                <option value="UPI">UPI</option>
                <option value="CARD">Card</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Currency</label>
              <input
                type="text"
                value={formData.currency}
                onChange={(e) => setFormData({...formData, currency: e.target.value})}
                className="clay-input"
                required
                maxLength={3}
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="clay-btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createAccount.isPending || updateAccount.isPending}
                className="clay-btn-primary"
              >
                {editingAccount ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

function AccountCard({ account, onEdit, onDelete, delay }) {
  const typeIcons = {
    BANK: '🏦',
    CASH: '💵',
    UPI: '📱',
    CARD: '💳',
  }

  return (
    <div
      className="glass-card p-6 reveal-on-scroll group cursor-pointer"
      style={{ animationDelay: delay }}
      onClick={() => onEdit(account)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-2xl shadow-clay-sm group-hover:scale-110 transition-transform duration-400">
          {typeIcons[account.type] || '🏦'}
        </div>
        <span className="clay-badge">{account.type}</span>
      </div>
      <h3 className="font-semibold text-ink-900 mb-1">{account.name}</h3>
      <p className="text-sm text-ink-500 mb-4">{account.id.slice(0, 8)}...</p>
      <div className="flex items-center justify-between pt-4 border-t border-ink-100">
        <span className="text-sm text-ink-500">Balance</span>
        <span className="text-xl font-bold text-ink-900">
          {formatCurrency(account.balance, account.currency)}
        </span>
      </div>
      <div className="flex justify-end space-x-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button
          onClick={(e) => { e.stopPropagation(); onEdit(account); }}
          className="clay-badge-info text-xs py-1.5 px-3"
        >
          Edit
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(account); }}
          className="clay-badge-danger text-xs py-1.5 px-3"
        >
          Delete
        </button>
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