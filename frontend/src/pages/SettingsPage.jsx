import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { formatCurrency } from '../utils/format'

export default function SettingsPage() {
  const { user, fetchUser } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    monthly_income: user?.monthly_income || 0,
    currency: user?.currency || 'INR',
  })
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setMessage({ type: '', text: '' })

    try {
      // In a real app, call API to update profile
      await fetchUser()
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to update profile' })
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setMessage({ type: '', text: '' })

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'Passwords do not match' })
      return
    }

    if (passwordData.new_password.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' })
      return
    }

    setSaving(true)

    try {
      // await api.post('/api/auth/change-password', passwordData)
      setMessage({ type: 'success', text: 'Password changed successfully!' })
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to change password' })
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    )},
    { id: 'security', label: 'Security', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
      </svg>
    )},
    { id: 'preferences', label: 'Preferences', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
      </svg>
    )},
  ]

  return (
    <div className="space-y-8">
      <div className="reveal-on-scroll">
        <h1 className="display-text mb-2">Settings</h1>
        <p className="subheading-text">Manage your account settings</p>
      </div>

      {/* Tabs */}
      <div className="glass-card reveal-on-scroll">
        <div className="border-b border-ink-100 px-6">
          <nav className="flex space-x-8" aria-label="Settings tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-all duration-400 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-700'
                    : 'border-transparent text-ink-500 hover:text-ink-700'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {message.text && (
            <div className={`mb-6 p-4 rounded-squircle ${
              message.type === 'success' ? 'bg-green-50 border border-green-200 text-green-800' : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              {message.text}
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit} className="space-y-5 max-w-md">
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  className="clay-input"
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="clay-input"
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Monthly Income</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.monthly_income}
                  onChange={(e) => setFormData({...formData, monthly_income: parseFloat(e.target.value) || 0})}
                  className="clay-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Currency</label>
                <input
                  type="text"
                  value={formData.currency}
                  onChange={(e) => setFormData({...formData, currency: e.target.value.toUpperCase()})}
                  className="clay-input"
                  maxLength={3}
                />
              </div>
              <button type="submit" disabled={saving} className="clay-btn-primary">
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          )}

          {activeTab === 'security' && (
            <form onSubmit={handlePasswordSubmit} className="space-y-5 max-w-md">
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Current Password</label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                  className="clay-input"
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">New Password</label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                  className="clay-input"
                  required
                  minLength={8}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-ink-700 mb-2 block">Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                  className="clay-input"
                  required
                />
              </div>
              <button type="submit" disabled={saving} className="clay-btn-primary">
                {saving ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          )}

          {activeTab === 'preferences' && (
            <div className="space-y-6 max-w-md">
              <div className="p-4 bg-white/30 rounded-squircle border border-white/40">
                <h3 className="font-medium text-ink-900 mb-4">Notification Preferences</h3>
                <div className="space-y-3">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input type="checkbox" className="w-5 h-5 rounded-clay text-primary-600 focus:ring-primary-500" defaultChecked />
                    <span className="text-ink-700">Budget breach alerts</span>
                  </label>
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input type="checkbox" className="w-5 h-5 rounded-clay text-primary-600 focus:ring-primary-500" defaultChecked />
                    <span className="text-ink-700">Goal achievement notifications</span>
                  </label>
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input type="checkbox" className="w-5 h-5 rounded-clay text-primary-600 focus:ring-primary-500" defaultChecked />
                    <span className="text-ink-700">Monthly insight ready</span>
                  </label>
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input type="checkbox" className="w-5 h-5 rounded-clay text-primary-600 focus:ring-primary-500" />
                    <span className="text-ink-700">Weekly spending summary</span>
                  </label>
                </div>
              </div>

              <div className="p-4 bg-white/30 rounded-squircle border border-white/40">
                <h3 className="font-medium text-ink-900 mb-4">Display Preferences</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-ink-700 mb-2 block">Default Currency</label>
                    <select className="clay-select" defaultValue={user?.currency || 'INR'}>
                      <option value="INR">INR (₹)</option>
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-ink-700 mb-2 block">Date Format</label>
                    <select className="clay-select" defaultValue="DD MMM YYYY">
                      <option value="DD MMM YYYY">DD MMM YYYY (e.g., 15 Jan 2024)</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD (e.g., 2024-01-15)</option>
                      <option value="MM/DD/YYYY">MM/DD/YYYY (e.g., 01/15/2024)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Account Info */}
      <div className="glass-card p-6 reveal-on-scroll">
        <h3 className="heading-text mb-6">Account Information</h3>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <dt className="text-sm text-ink-500">User ID</dt>
            <dd className="font-mono text-sm text-ink-900 mt-1">{user?.id}</dd>
          </div>
          <div>
            <dt className="text-sm text-ink-500">Role</dt>
            <dd className="font-medium text-ink-900 mt-1 capitalize">{user?.role?.toLowerCase()}</dd>
          </div>
          <div>
            <dt className="text-sm text-ink-500">Member Since</dt>
            <dd className="text-sm text-ink-900 mt-1">{user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</dd>
          </div>
          <div>
            <dt className="text-sm text-ink-500">Status</dt>
            <dd className="font-medium text-ink-900 mt-1">{user?.is_active ? 'Active' : 'Inactive'}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}