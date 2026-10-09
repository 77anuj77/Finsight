import { useState, useEffect, useRef } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const menuRef = useRef(null)

  // Handle scroll
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close menu on resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) setIsMenuOpen(false)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsMenuOpen(false)
      }
    }
    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isMenuOpen])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    )},
    { path: '/accounts', label: 'Accounts', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="2" y="5" width="20" height="14" rx="2" />
        <line x1="2" y1="10" x2="22" y2="10" />
      </svg>
    )},
    { path: '/transactions', label: 'Transactions', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    )},
    { path: '/budgets', label: 'Budgets', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
        <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
        <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
      </svg>
    )},
    { path: '/goals', label: 'Goals', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="6" />
        <circle cx="12" cy="12" r="2" />
      </svg>
    )},
    { path: '/analytics', label: 'Analytics', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M3 3v18h18" />
        <path d="M18 17V9" />
        <path d="M13 17V5" />
        <path d="M8 17v-3" />
      </svg>
    )},
    { path: '/insights', label: 'Insights', icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 2a7 7 0 0 1 7 7c0 5-7 13-7 13S5 14 5 9a7 7 0 0 1 7-7z" />
        <circle cx="12" cy="9" r="2.5" />
      </svg>
    )},
  ]

  return (
    <>
      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden glass-overlay animate-fade-in"
          aria-hidden="true"
        />
      )}

      {/* Desktop Nav - Floating Glass Pill */}
      <nav
        ref={menuRef}
        className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-2rem)] max-w-6xl transition-all duration-600 ${
          scrolled ? 'top-2' : 'top-6'
        }`}
        role="navigation"
        aria-label="Main navigation"
      >
        <div className={`
          backdrop-blur-2xl
          bg-white/70
          border border-white/40
          rounded-full
          px-6 py-3
          shadow-glass-lg
          transition-all duration-600
          ${scrolled ? 'bg-white/80 shadow-glass-xl' : ''}
        `}>
          <div className="flex items-center justify-between">
            {/* Logo */}
            <NavLink
              to="/dashboard"
              className="flex items-center space-x-3 group"
              aria-label="FinSight Home"
            >
              <div className="relative w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-clay-sm group-hover:scale-105 transition-transform duration-400">
                <span className="text-lg">💰</span>
                <div className="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-400" />
              </div>
              <span className="font-display font-bold text-xl text-ink-900 tracking-tight">
                FinSight
              </span>
            </NavLink>

            {/* Desktop Nav Links */}
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item, i) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/dashboard'}
                  className={({ isActive }) => `
                    relative flex items-center space-x-2 px-4 py-2.5 rounded-full text-sm font-medium
                    transition-all duration-400 focus-ring
                    ${isActive
                      ? 'text-primary-700 bg-primary-50 shadow-clay-sm'
                      : 'text-ink-600 hover:text-ink-900 hover:bg-white/50'
                    }
                  `}
                  style={{ animationDelay: `${i * 0.05}s` }}
                >
                  <span className={`transition-transform duration-400 ${isActive ? 'scale-110' : ''}`}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                  {isActive && (
                    <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-primary-500" />
                  )}
                </NavLink>
              ))}
            </div>

            {/* User Menu - Desktop */}
            <div className="hidden md:flex items-center space-x-3">
              <div className="flex items-center space-x-3 pr-3 py-1.5 rounded-full bg-white/50 border border-white/30">
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-xs font-bold shadow-clay-sm">
                  {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-ink-900 leading-none">
                    {user?.full_name?.split(' ')[0] || 'User'}
                  </span>
                  <span className="text-[10px] text-ink-500 capitalize mt-0.5">{user?.role?.toLowerCase()}</span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="clay-btn-secondary text-sm py-2 px-4"
                aria-label="Logout"
              >
                Logout
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden relative w-10 h-10 rounded-full bg-white/50 border border-white/30 flex items-center justify-center focus-ring"
              aria-expanded={isMenuOpen}
              aria-label="Toggle menu"
              aria-controls="mobile-menu"
            >
              <div className="relative w-5 h-4">
                <span className={`absolute w-5 h-0.5 bg-ink-700 rounded-full transition-all duration-400 ${
                  isMenuOpen ? 'top-1.5 rotate-45' : 'top-0'
                }`} />
                <span className={`absolute w-5 h-0.5 bg-ink-700 rounded-full transition-all duration-400 ${
                  isMenuOpen ? 'top-1.5 -rotate-45' : 'top-2'
                }`} />
              </div>
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        id="mobile-menu"
        className={`
          fixed top-0 right-0 z-50 w-80 max-w-[85vw] h-full
          backdrop-blur-3xl bg-white/90 border-l border-white/30
          shadow-2xl
          transition-all duration-500
          ${isMenuOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <div className="flex flex-col h-full p-6 pt-20">
          {/* Mobile User Info */}
          <div className="flex items-center space-x-3 mb-8 pb-6 border-b border-white/20">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-lg font-bold shadow-clay">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div>
              <p className="font-semibold text-ink-900">{user?.full_name}</p>
              <p className="text-sm text-ink-500 capitalize">{user?.role?.toLowerCase()}</p>
            </div>
          </div>

          {/* Mobile Nav Links */}
          <nav className="flex-1 space-y-2">
            {navItems.map((item, i) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/dashboard'}
                onClick={() => setIsMenuOpen(false)}
                className={({ isActive }) => `
                  flex items-center space-x-4 px-4 py-3.5 rounded-squircle
                  transition-all duration-400 focus-ring
                  ${isActive
                    ? 'bg-primary-50 text-primary-700 shadow-clay-sm'
                    : 'text-ink-600 hover:bg-white/50'
                  }
                `}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <span className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-ink-400'}`}>
                  {item.icon}
                </span>
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <span className="ml-auto w-2 h-2 rounded-full bg-primary-500" />
                )}
              </NavLink>
            ))}
          </nav>

          {/* Mobile Logout */}
          <button
            onClick={() => {
              handleLogout()
              setIsMenuOpen(false)
            }}
            className="clay-btn-danger w-full mt-6"
            aria-label="Logout"
          >
            Logout
          </button>
        </div>
      </div>
    </>
  )
}