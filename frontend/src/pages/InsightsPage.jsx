import { useState } from 'react'
import { useLatestInsight, useGenerateInsight, useInsightsHistory } from '../hooks/useApi'
import { formatDate, getMonthName } from '../utils/format'

export default function InsightsPage() {
  const [month, setMonth] = useState(new Date())
  const monthKey = getMonthName(month)

  const { data: insight, isLoading: insightLoading } = useLatestInsight(monthKey)
  const generateInsight = useGenerateInsight()
  const { data: history } = useInsightsHistory(12)

  const handleGenerate = async () => {
    await generateInsight.mutateAsync(monthKey)
  }

  const handleMonthChange = (delta) => {
    const newMonth = new Date(month)
    newMonth.setMonth(newMonth.getMonth() + delta)
    setMonth(newMonth)
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="reveal-on-scroll">
          <h1 className="display-text mb-2">AI Insights</h1>
          <p className="subheading-text">Smart financial analysis and recommendations</p>
        </div>
        <div className="flex items-center space-x-4 reveal-on-scroll" style={{ animationDelay: '0.1s' }}>
          <button onClick={() => handleMonthChange(-1)} className="clay-btn-secondary">← Previous</button>
          <span className="text-lg font-semibold text-ink-900 min-w-[200px] text-center">{monthKey}</span>
          <button onClick={() => handleMonthChange(1)} className="clay-btn-secondary" disabled={new Date(monthKey) > new Date()}>Next →</button>
          <button
            onClick={handleGenerate}
            disabled={generateInsight.isPending}
            className="clay-btn-primary ml-4"
          >
            {generateInsight.isPending ? 'Generating...' : 'Generate Insight'}
          </button>
        </div>
      </div>

      {/* Current Insight */}
      <div className="glass-card p-8 reveal-on-scroll">
        <div className="flex items-center justify-between mb-6">
          <h3 className="heading-text">Monthly Insight</h3>
          {insight?.generated_at && (
            <span className="text-sm text-ink-500">
              Generated: {formatDate(insight.generated_at, 'dd MMM yyyy, HH:mm')}
            </span>
          )}
        </div>

        {insightLoading ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
          </div>
        ) : insight ? (
          <div className="space-y-6">
            {/* Summary */}
            <div className="prose prose-ink max-w-none">
              <p className="text-ink-700 leading-relaxed text-lg">{insight.summary}</p>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-white/30 rounded-squircle border border-white/40">
              <MetricItem label="Total Income" value={insight.metrics?.total_income} />
              <MetricItem label="Total Expenses" value={insight.metrics?.total_expense} />
              <MetricItem label="Net Savings" value={insight.metrics?.net_savings} />
              <MetricItem label="Savings Rate" value={`${insight.metrics?.savings_rate?.toFixed(1)}%`} />
            </div>

            {/* Recommendations */}
            {insight.recommendations?.length > 0 && (
              <div>
                <h4 className="font-semibold text-ink-900 mb-3 flex items-center space-x-2">
                  <span>💡</span>
                  <span>Recommendations</span>
                </h4>
                <ul className="space-y-2">
                  {insight.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start space-x-3 p-4 bg-primary-50/50 rounded-squircle border border-primary-100">
                      <span className="text-primary-600 font-bold">→</span>
                      <span className="text-ink-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Warnings */}
            {insight.warnings?.length > 0 && (
              <div>
                <h4 className="font-semibold text-ink-900 mb-3 flex items-center space-x-2">
                  <span>⚠️</span>
                  <span>Warnings</span>
                </h4>
                <ul className="space-y-2">
                  {insight.warnings.map((warn, i) => (
                    <li key={i} className="flex items-start space-x-3 p-4 bg-red-50/50 rounded-squircle border border-red-100">
                      <span className="text-red-600 font-bold">!</span>
                      <span className="text-red-800">{warn}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-ink-500 mb-4">No insight generated for this month yet</p>
            <button onClick={handleGenerate} className="clay-btn-primary" disabled={generateInsight.isPending}>
              {generateInsight.isPending ? 'Generating...' : 'Generate Insight'}
            </button>
          </div>
        )}
      </div>

      {/* History */}
      <div className="glass-card p-6 reveal-on-scroll">
        <h3 className="heading-text mb-6">Insight History</h3>
        {history?.length > 0 ? (
          <div className="space-y-3">
            {history.map((item, i) => (
              <div key={i} className="p-4 bg-white/30 rounded-squircle border border-white/40 hover:bg-white/40 transition-colors duration-300 cursor-pointer">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-ink-900">{getMonthName(new Date(item.month_key + '-01'))}</p>
                    <p className="text-sm text-ink-500">
                      Generated: {formatDate(item.generated_at, 'dd MMM yyyy, HH:mm')}
                    </p>
                  </div>
                  <span className="clay-badge-info">View</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-ink-500 text-center py-8">No insight history yet</p>
        )}
      </div>
    </div>
  )
}

function MetricItem({ label, value }) {
  return (
    <div className="text-center">
      <p className="text-xs text-ink-500 uppercase tracking-wide">{label}</p>
      <p className="text-lg font-bold text-ink-900 mt-1">{value}</p>
    </div>
  )
}