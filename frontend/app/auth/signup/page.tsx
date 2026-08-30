'use client'

import { useState } from 'react'
import Link from 'next/link'
import { FiMail, FiLock, FiUser, FiLoader, FiArrowRight, FiSend, FiRefreshCw, FiCheckCircle } from 'react-icons/fi'
import { apiClient } from '@/lib/api/client'

export default function SignupPage() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)
  const [resent, setResent] = useState(false)
  const [error, setError] = useState('')
  const [passwordStrength, setPasswordStrength] = useState(0)
  const [accountCreated, setAccountCreated] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))

    if (name === 'password') {
      let strength = 0
      if (value.length >= 8) strength++
      if (/[a-z]/.test(value) && /[A-Z]/.test(value)) strength++
      if (/\d/.test(value)) strength++
      if (/[^a-zA-Z\d]/.test(value)) strength++
      setPasswordStrength(strength)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    if (formData.password.length > 72) {
      setError('Password must not exceed 72 characters')
      return
    }

    setLoading(true)

    try {
      await apiClient.signup(formData.email, formData.password, formData.fullName)
      setAccountCreated(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setError('')
    setResending(true)
    try {
      await apiClient.resendVerification(formData.email)
      setResent(true)
      setTimeout(() => setResent(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend link')
    } finally {
      setResending(false)
    }
  }

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 0) return 'bg-stone-200'
    if (passwordStrength === 1) return 'bg-red-400'
    if (passwordStrength === 2) return 'bg-amber-400'
    if (passwordStrength === 3) return 'bg-indigo-400'
    return 'bg-emerald-500'
  }

  const getPasswordStrengthText = () => {
    if (passwordStrength === 0) return ''
    if (passwordStrength === 1) return 'Weak'
    if (passwordStrength === 2) return 'Fair'
    if (passwordStrength === 3) return 'Good'
    return 'Strong'
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#faf7f2] via-[#f5f1e9] to-[#faf7f2] p-4 relative overflow-hidden">
      <div className="absolute top-0 -left-32 w-96 h-96 bg-emerald-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 -right-32 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"></div>

      <div className="w-full max-w-md z-10 animate-fadeIn">
        <div className="bg-white/90 backdrop-blur-xl border border-black/[0.06] rounded-2xl shadow-xl shadow-black/[0.04] p-8 transition-all duration-300">
          {!accountCreated ? (
            <>
              <div className="mb-8 text-center">
                <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-emerald-600 rounded-xl shadow-lg shadow-emerald-600/20">
                  <FiUser className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-stone-900 mb-1.5">Create account</h1>
                <p className="text-stone-500 text-sm">Join IT-Gate and start analyzing documents</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1.5">Full name</label>
                  <div className="relative group">
                    <FiUser className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      placeholder="John Doe"
                      required
                      className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 transition-all duration-200"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1.5">Email address</label>
                  <div className="relative group">
                    <FiMail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      required
                      className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 transition-all duration-200"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1.5">Password</label>
                  <div className="relative group">
                    <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      maxLength={72}
                      required
                      className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 transition-all duration-200"
                    />
                  </div>
                  {formData.password && (
                    <div className="mt-2 animate-fadeIn">
                      <div className="flex gap-1 mb-1">
                        {[...Array(4)].map((_, i) => (
                          <div
                            key={i}
                            className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                              i < passwordStrength ? getPasswordStrengthColor() : 'bg-stone-200'
                            }`}
                          />
                        ))}
                      </div>
                      <p className="text-xs text-stone-500">
                        Password strength: <span className="text-stone-700 font-semibold">{getPasswordStrengthText()}</span>
                      </p>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1.5">Confirm password</label>
                  <div className="relative group">
                    <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="••••••••"
                      maxLength={72}
                      required
                      className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 transition-all duration-200"
                    />
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-xl text-sm animate-fadeIn">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full mt-6 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-emerald-600/25 hover:shadow-xl hover:shadow-emerald-600/30"
                >
                  {loading ? (
                    <>
                      <FiLoader className="animate-spin w-5 h-5" />
                      <span>Creating account...</span>
                    </>
                  ) : (
                    <>
                      <span>Create account</span>
                      <FiArrowRight className="w-4.5 h-4.5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>

              <p className="text-center text-stone-500 mt-6 text-sm">
                Already have an account?{' '}
                <Link href="/auth/login" className="text-emerald-600 font-semibold hover:text-emerald-700 transition-colors">
                  Sign in
                </Link>
              </p>
            </>
          ) : (
            <div className="text-center">
              <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-emerald-100 rounded-xl">
                <FiSend className="w-5 h-5 text-emerald-600" />
              </div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1.5">Check your email</h1>
              <p className="text-stone-500 text-sm mb-1">
                We sent a verification link to
              </p>
              <p className="text-stone-800 font-medium text-sm mb-6">{formData.email}</p>
              <p className="text-stone-500 text-xs mb-6">
                Click the link in the email to activate your account. The link expires in 10 minutes.
              </p>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-xl text-sm mb-4 animate-fadeIn">
                  {error}
                </div>
              )}

              <button
                onClick={handleResend}
                disabled={resending}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-xl text-sm text-stone-700 font-medium transition-all disabled:opacity-50"
              >
                {resending ? (
                  <FiLoader className="w-4 h-4 animate-spin" />
                ) : resent ? (
                  <FiCheckCircle className="w-4 h-4 text-emerald-600" />
                ) : (
                  <FiRefreshCw className="w-4 h-4" />
                )}
                {resent ? 'Link sent!' : 'Resend verification email'}
              </button>

              <p className="text-center text-stone-500 mt-6 text-sm">
                <Link href="/auth/login" className="text-emerald-600 font-semibold hover:text-emerald-700 transition-colors">
                  Back to login
                </Link>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}