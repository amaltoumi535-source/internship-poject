'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FiMail, FiLock, FiHash, FiLoader, FiArrowRight, FiArrowLeft, FiCheckCircle } from 'react-icons/fi'
import { apiClient } from '@/lib/api/client'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [emailSent, setEmailSent] = useState(false)
  const [sending, setSending] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const router = useRouter()

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSending(true)
    try {
      await apiClient.forgotPassword(email)
      setEmailSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset code')
    } finally {
      setSending(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setResetting(true)
    try {
      await apiClient.resetPassword(email, code, newPassword)
      setSuccess(true)
      setTimeout(() => router.push('/auth/login'), 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset failed')
    } finally {
      setResetting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#faf7f2] via-[#f5f1e9] to-[#faf7f2] p-4 relative overflow-hidden">
      <div className="absolute top-0 -left-32 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 -right-32 w-96 h-96 bg-amber-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>

      <div className="w-full max-w-md z-10 animate-fadeIn">
        <div className="bg-white/90 backdrop-blur-xl border border-black/[0.06] rounded-2xl shadow-xl shadow-black/[0.04] p-8">
          {success ? (
            <div className="text-center py-4">
              <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-emerald-100 rounded-xl">
                <FiCheckCircle className="w-6 h-6 text-emerald-600" />
              </div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1.5">Password reset</h1>
              <p className="text-stone-500 text-sm">Redirecting you to sign in...</p>
            </div>
          ) : (
            <>
              <div className="mb-8 text-center">
                <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/20">
                  <FiLock className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-stone-900 mb-1.5">Reset password</h1>
                <p className="text-stone-500 text-sm">
                  {emailSent
                    ? 'Enter the code we sent you and your new password'
                    : "We'll email you a code to reset your password"}
                </p>
              </div>

              <form onSubmit={emailSent ? handleResetPassword : handleSendCode} className="space-y-4">
                {/* Email — disabled once code is sent */}
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1.5">Email address</label>
                  <div className="relative group">
                    <FiMail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      disabled={emailSent}
                      className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
                    />
                  </div>
                </div>

                {emailSent && (
                  <>
                    {/* Code */}
                    <div className="animate-fadeIn">
                      <label className="block text-sm font-medium text-stone-700 mb-1.5">Reset code</label>
                      <div className="relative group">
                        <FiHash className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-indigo-500 transition-colors" />
                        <input
                          type="text"
                          value={code}
                          onChange={(e) => setCode(e.target.value)}
                          placeholder="6-digit code"
                          maxLength={6}
                          required
                          className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200 tracking-widest"
                        />
                      </div>
                    </div>

                    {/* New password */}
                    <div className="animate-fadeIn">
                      <label className="block text-sm font-medium text-stone-700 mb-1.5">New password</label>
                      <div className="relative group">
                        <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-indigo-500 transition-colors" />
                        <input
                          type="password"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="••••••••"
                          maxLength={72}
                          required
                          className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200"
                        />
                      </div>
                    </div>

                    {/* Confirm password */}
                    <div className="animate-fadeIn">
                      <label className="block text-sm font-medium text-stone-700 mb-1.5">Confirm password</label>
                      <div className="relative group">
                        <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-indigo-500 transition-colors" />
                        <input
                          type="password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="••••••••"
                          maxLength={72}
                          required
                          className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200"
                        />
                      </div>
                    </div>
                  </>
                )}

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-xl text-sm animate-fadeIn">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={sending || resetting}
                  className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-indigo-600/25 hover:shadow-xl hover:shadow-indigo-600/30"
                >
                  {sending || resetting ? (
                    <>
                      <FiLoader className="animate-spin w-5 h-5" />
                      <span>{emailSent ? 'Resetting...' : 'Sending...'}</span>
                    </>
                  ) : (
                    <>
                      <span>{emailSent ? 'Reset password' : 'Send reset code'}</span>
                      <FiArrowRight className="w-4.5 h-4.5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>
            </>
          )}
        </div>

        {!success && (
          <p className="text-center text-stone-500 mt-6 text-sm">
            <Link href="/auth/login" className="text-indigo-600 font-semibold hover:text-indigo-700 transition-colors inline-flex items-center gap-1.5">
              <FiArrowLeft className="w-3.5 h-3.5" />
              Back to login
            </Link>
          </p>
        )}
      </div>
    </div>
  )
}