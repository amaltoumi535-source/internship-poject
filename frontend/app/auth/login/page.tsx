'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FiMail, FiLock, FiLoader, FiArrowRight, FiFileText } from 'react-icons/fi'
import { apiClient } from '@/lib/api/client'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await apiClient.signin(formData.email, formData.password)
      router.push('/chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#faf7f2] via-[#f5f1e9] to-[#faf7f2] p-4 relative overflow-hidden">
      {/* Soft ambient shapes, warm and subtle */}
      <div className="absolute top-0 -left-32 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 -right-32 w-96 h-96 bg-amber-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>

      <div className="w-full max-w-md z-10 animate-fadeIn">
        <div className="bg-white/90 backdrop-blur-xl border border-black/[0.06] rounded-2xl shadow-xl shadow-black/[0.04] p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-black/[0.06]">
          <div className="mb-8 text-center">
            <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-600/20">
              <FiFileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-stone-900 mb-1.5">Welcome back</h1>
            <p className="text-stone-500 text-sm">Sign in to your IT-Gate Agent</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Input */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">Email address</label>
              <div className="relative group">
                <FiMail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-indigo-500 transition-colors" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  required
                  className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1.5">Password</label>
              <div className="relative group">
                <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400 w-4.5 h-4.5 group-focus-within:text-indigo-500 transition-colors" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  required
                  className="w-full pl-11 pr-4 py-2.5 bg-stone-50 border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all duration-200"
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2.5 rounded-xl text-sm animate-fadeIn">
                {error}
              </div>
            )}

            {/* Remember & Forgot Password */}
            <div className="flex items-center justify-between text-sm pt-1">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input type="checkbox" className="w-4 h-4 accent-indigo-600 rounded border-stone-300" />
                <span className="text-stone-500 group-hover:text-stone-700 transition-colors">Remember me</span>
              </label>
              <Link href="/auth/forgot-password" className="text-indigo-600 hover:text-indigo-700 font-medium transition-colors">
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group shadow-lg shadow-indigo-600/25 hover:shadow-xl hover:shadow-indigo-600/30"
            >
              {loading ? (
                <>
                  <FiLoader className="animate-spin w-5 h-5" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign in</span>
                  <FiArrowRight className="w-4.5 h-4.5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Sign Up Link */}
        <p className="text-center text-stone-500 mt-6 text-sm">
          Don't have an account?{' '}
          <Link
            href="/auth/signup"
            className="text-indigo-600 font-semibold hover:text-indigo-700 transition-colors"
          >
            Create one now
          </Link>
        </p>
      </div>
    </div>
  )
}