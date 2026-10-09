import { useState } from 'react'
import { useTransactions, useCreateTransaction, useUpdateTransaction, useDeleteTransaction, useConfirmTransaction } from '../hooks/useApi'
import { formatCurrency, formatDate, formatRelativeTime } from '../utils/format'

const TYPE_COLORS = {
  INCOME: { text: 'text-green-600', badge: 'clay-badge-success' },
  EXPENSE: { text: 'text-red-600', badge: 'clay-badge-danger' },
  TRANSFER: { text: 'text-blue-600', badge: 'clay-badge-info' },
}

const FLAG_COLORS = {
  NORMAL: 'clay-badge',
  SUSPICIOUS: 'clay-badge-danger',
  REJECTED: 'clay-badge-danger',
  CONFIRMED: 'clay-badge-success',
  REVIEW: 'clay-badge-warning',
}

export default function TransactionsPage() {
  const [showModal, setShowModal] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    type: '',
    category_id: '',
    flag_status: '',
  })
  const [formData, setFormData] = useState({
    account_id: '',
    category_id: 2,
    type: 'EXPENSE',
    amount: '',
    payee: '',
    transacted_at: new Date().toISOString().slice(0, 16),
    notes: '',
  })

  const { data: result, isLoading, refetch } = useTransactions(filters)
  const createTransaction = useCreateTransaction()
  const updateTransaction = useUpdateTransaction()
  const deleteTransaction = useDeleteTransaction()
  const confirmTransaction = useConfirmTransaction()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingTransaction) {
        await updateTransaction.mutateAsync({ id: editingTransaction.id, data: formData })
      } else {
        await createTransaction.mutateAsync(formData)
      }
      setShowModal(false)
      resetForm()
      refetch()
    } catch (err) {
      console.error('Error saving transaction:', err)
    }
  }

  const handleEdit = (txn) => {
    setEditingTransaction(txn)
    setFormData({
      account_id: txn.account_id,
      category_id: txn.category_id,
      type: txn.type,
      amount: txn.amount,
      payee: txn.payee || '',
      transacted_at: txn.transacted_at?.slice(0, 16) || new Date().toISOString().slice(0, 16),
      notes: txn.notes || '',
    })
    setShowModal(true)
  }

  const handleDelete = async (txn) => {
    if (window.confirm(`Delete transaction "${txn.payee || 'Unknown'}"?`)) {
      try {
        await deleteTransaction.mutateAsync(txn.id)
        refetch()
      } catch (err) {
        console.error('Error deleting transaction:', err)
      }
    }
  }

  const handleConfirm = async (txn, decision) => {
    try {
      await confirmTransaction.mutateAsync({ id: txn.id, decision })
      refetch()
    } catch (err) {
      console.error('Error confirming transaction:', err)
    }
  }

  const handleNew = () => {
    setEditingTransaction(null)
    resetForm()
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({
      account_id: '',
      category_id: 2,
      type: 'EXPENSE',
      amount: '',
      payee: '',
      transacted_at: new Date().toISOString().slice(0, 16),
      notes: '',
    })
    setEditingTransaction(null)
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div></div>
  }

  const transactions = result?.items || []
  const total = result?.total || 0
  const pages = result?.pages || 1

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">Transactions</h1>
          <p className="subheading-text">View and manage your transactions</p>
        </div>
        <button
          onClick={handleNew}
          className="clay-btn-primary reveal-on-scroll"
          style={{ animationDelay: '0.1s' }}
        >
          Add Transaction
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-6 reveal-on-scroll">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium text-ink-700 mb-2 block">Type</label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
              className="clay-select"
            >
              <option value="">All Types</option>
              <option value="INCOME">Income</option>
              <option value="EXPENSE">Expense</option>
              <option value="TRANSFER">Transfer</option>
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium text-ink-700 mb-2 block">Category</label>
            <select
              value={filters.category_id}
              onChange={(e) => handleFilterChange('category_id', e.target.value)}
              className="clay-select"
            >
              <option value="">All Categories</option>
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
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm font-medium text-ink-700 mb-2 block">Flag Status</label>
            <select
              value={filters.flag_status}
              onChange={(e) => handleFilterChange('flag_status', e.target.value)}
              className="clay-select"
            >
              <option value="">All Statuses</option>
              <option value="NORMAL">Normal</option>
              <option value="SUSPICIOUS">Suspicious</option>
              <option value="REVIEW">Review</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {/* Transactions List */}
      <div className="glass-card overflow-hidden reveal-on-scroll">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm font-medium text-ink-500 border-b border-ink-100">
                <th className="pb-4 px-6">Date</th>
                <th className="pb-4 px-6">Payee</th>
                <th className="pb-4 px-6">Category</th>
                <th className="pb-4 px-6">Type</th>
                <th className="pb-4 px-6 text-right">Amount</th>
                <th className="pb-4 px-6">Status</th>
                <th className="pb-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100">
              {transactions.map((txn, i) => (
                <tr
                  key={txn.id}
                  className="hover:bg-white/30 transition-colors duration-300"
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <td className="py-4 px-6">
                    <div className="text-sm text-ink-900">{formatDate(txn.transacted_at)}</div>
                    <div className="text-xs text-ink-500">{formatRelativeTime(txn.transacted_at)}</div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="font-medium text-ink-900">{txn.payee || '—'}</div>
                    {txn.notes && <div className="text-xs text-ink-500 truncate max-w-xs">{txn.notes}</div>}
                  </td>
                  <td className="py-4 px-6">
                    <span className="text-sm text-ink-600">Category {txn.category_id}</span>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`clay-badge ${TYPE_COLORS[txn.type]?.badge || 'clay-badge'}`}>
                      {txn.type}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <span className={`font-semibold ${TYPE_COLORS[txn.type]?.text || 'text-ink-900'}`}>
                      {txn.type === 'INCOME' ? '+' : txn.type === 'EXPENSE' ? '-' : ''}
                      {formatCurrency(txn.amount)}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`clay-badge ${FLAG_COLORS[txn.flag_status] || 'clay-badge'}`}>
                      {txn.flag_status}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      {txn.flag_status === 'SUSPICIOUS' || txn.flag_status === 'REVIEW' ? (
                        <>
                          <button
                            onClick={() => handleConfirm(txn, 'CONFIRMED')}
                            className="clay-badge-success text-xs py-1.5 px-3"
                            disabled={confirmTransaction.isPending}
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => handleConfirm(txn, 'REJECTED')}
                            className="clay-badge-danger text-xs py-1.5 px-3"
                            disabled={confirmTransaction.isPending}
                          >
                            Reject
                          </button>
                        </>
                      ) : (
                        <>
                          <button onClick={() => handleEdit(txn)} className="clay-badge-info text-xs py-1.5 px-3">Edit</button>
                          <button onClick={() => handleDelete(txn)} className="clay-badge-danger text-xs py-1.5 px-3">Delete</button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {transactions.length === 0 && (
          <div className="text-center py-12">
            <p className="text-ink-500">No transactions found. Click "Add Transaction" to create one.</p>
          </div>
        )}

        {/* Pagination */}
        {pages > 1 && (
          <div className="p-4 flex items-center justify-between border-t border-ink-100">
            <p className="text-sm text-ink-600">
              Showing {((filters.page - 1) * filters.size) + 1} to {Math.min(filters.page * filters.size, total)} of {total}
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setFilters(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={filters.page === 1}
                className="clay-btn-secondary text-sm"
              >
                Previous
              </button>
              <button
                onClick={() => setFilters(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={filters.page === pages}
                className="clay-btn-secondary text-sm"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <Modal
          title={editingTransaction ? 'Edit Transaction' : 'Add Transaction'}
          onClose={() => setShowModal(false)}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Account</label>
              <select
                value={formData.account_id}
                onChange={(e) => setFormData({...formData, account_id: e.target.value})}
                className="clay-select"
                required
              >
                <option value="">Select Account</option>
                {/* In real app, populate from accounts API */}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value})}
                  className="clay-select"
                  required
                >
                  <option value="EXPENSE">Expense</option>
                  <option value="INCOME">Income</option>
                  <option value="TRANSFER">Transfer</option>
                </select>
              </div>
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
                  <option value={0}>Transfer</option>
                </select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Amount</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({...formData, amount: e.target.value})}
                className="clay-input"
                required
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Payee</label>
              <input
                type="text"
                value={formData.payee}
                onChange={(e) => setFormData({...formData, payee: e.target.value})}
                className="clay-input"
                placeholder="e.g., Zomato, Uber"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Date & Time</label>
              <input
                type="datetime-local"
                value={formData.transacted_at}
                onChange={(e) => setFormData({...formData, transacted_at: e.target.value})}
                className="clay-input"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-ink-700 mb-2 block">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="clay-input"
                rows={2}
                placeholder="Optional notes"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={() => setShowModal(false)} className="clay-btn-secondary">Cancel</button>
              <button type="submit" disabled={createTransaction.isPending || updateTransaction.isPending} className="clay-btn-primary">
                {editingTransaction ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </Modal>
      )}
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