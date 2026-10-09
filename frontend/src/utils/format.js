import { format, formatDistanceToNow } from 'date-fns'

export function formatCurrency(amount, currency = 'INR') {
  if (amount === null || amount === undefined) return '₹0.00'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return new Intl.NumberFormat('en-IN').format(num)
}

export function formatDate(dateString, pattern = 'dd MMM yyyy') {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return format(date, pattern)
  } catch {
    return ''
  }
}

export function formatDateTime(dateString) {
  return formatDate(dateString, 'dd MMM yyyy, HH:mm')
}

export function formatRelativeTime(dateString) {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return formatDistanceToNow(date, { addSuffix: true })
  } catch {
    return ''
  }
}

export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '0%'
  return `${value.toFixed(decimals)}%`
}

export function getMonthKey(date = new Date()) {
  return format(date, 'yyyy-MM')
}

export function getMonthName(date = new Date()) {
  return format(date, 'MMMM yyyy')
}

export function getPreviousMonth(date = new Date()) {
  const d = new Date(date)
  d.setMonth(d.getMonth() - 1)
  return d
}

export function getNextMonth(date = new Date()) {
  const d = new Date(date)
  d.setMonth(d.getMonth() + 1)
  return d
}

export function truncateText(text, maxLength = 30) {
  if (!text || text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}