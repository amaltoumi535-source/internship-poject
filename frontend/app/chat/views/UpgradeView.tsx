'use client'

import { FiCheck, FiZap } from 'react-icons/fi'

interface Plan {
  name: string
  price: string
  period: string
  highlight?: boolean
  features: string[]
}

const PLANS: Plan[] = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    features: ['20 documents / month', 'Basic OCR', 'Community support'],
  },
  {
    name: 'Pro',
    price: '$19',
    period: '/month',
    highlight: true,
    features: ['Unlimited documents', 'Advanced OCR + vector search', 'Priority processing', 'Email support'],
  },
  {
    name: 'Team',
    price: '$49',
    period: '/user/month',
    features: ['Everything in Pro', 'Shared projects', 'Admin controls', 'Priority support'],
  },
]

export default function UpgradeView() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="border-b border-[var(--border-subtle)] bg-[var(--surface)] backdrop-blur-xl px-6 py-4">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Upgrade plan</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="text-center mb-8">
          <div className="inline-block p-3 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-2xl mb-3">
            <FiZap className="w-6 h-6 text-blue-400" />
          </div>
          <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-1">Choose the plan that fits your workflow</h2>
          <p className="text-sm text-[var(--text-muted)]">Cancel anytime. Prices shown are placeholders.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-4xl mx-auto">
          {PLANS.map(plan => (
            <div
              key={plan.name}
              className={`relative rounded-2xl p-6 border transition-all ${
                plan.highlight
                  ? 'bg-gradient-to-b from-blue-600/20 to-purple-600/10 border-blue-500/50 shadow-lg shadow-blue-500/20'
                  : 'bg-[var(--surface-soft)] border-[var(--border-subtle)]'
              }`}
            >
              {plan.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs font-semibold rounded-full">
                  Most popular
                </span>
              )}
              <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2 mb-4">
                <span className="text-3xl font-bold text-[var(--text-primary)]">{plan.price}</span>
                <span className="text-sm text-[var(--text-muted)]">{plan.period}</span>
              </div>
              <ul className="space-y-2.5 mb-6">
                {plan.features.map(f => (
                  <li key={f} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                    <FiCheck className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <button
                className={`w-full py-2.5 rounded-xl text-sm font-medium transition-all ${
                  plan.highlight
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-[var(--surface-strong)] hover:bg-[var(--surface-hover-strong)] border border-[var(--border-strong)] text-[var(--text-primary)]'
                }`}
              >
                {plan.name === 'Free' ? 'Current plan' : `Choose ${plan.name}`}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}