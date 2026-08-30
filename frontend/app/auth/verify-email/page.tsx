'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { FiCheckCircle, FiXCircle, FiLoader, FiArrowLeft } from 'react-icons/fi'
import { apiClient } from '@/lib/api/client'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [error, setError] = useState('')
  const hasRun = useRef(false)

  useEffect(() => {
    if (hasRun.current) return
    hasRun.current = true

    const email = searchParams.get('email')
    const code = searchParams.get('code')

    if (!email || !code) {
      setStatus('error')
      setError('This verification link is invalid.')
      return
    }

    async function verify() {
      try {
        await apiClient.verifyEmail(email!, code!)
        setStatus('success')
        setTimeout(() => router.push('/chat'), 1500)
      } catch (err) {
        setStatus('error')
        setError(err instanceof Error ? err.message : 'Verification failed')
      }
    }

    verify()
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#faf7f2] via-[#f5f1e9] to-[#faf7f2] p-4 relative overflow-hidden">
      <div className="absolute top-0 -left-32 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 -right-32 w-96 h-96 bg-amber-100 rounded-full mix-blend-multiply filter blur-3xl opacity-40"></div>

      <div className="w-full max-w-md z-10 animate-fadeIn">
        <div className="bg-white/90 backdrop-blur-xl border border-black/[0.06] rounded-2xl shadow-xl shadow-black/[0.04] p-8 text-center">
          {status === 'verifying' && (
            <>
              <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-indigo-100 rounded-xl">
                <FiLoader className="w-6 h-6 text-indigo-600 animate-spin" />
              </div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1.5">Verifying your email...</h1>
              <p className="text-stone-500 text-sm">This will just take a moment.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-emerald-100 rounded-xl">
                <FiCheckCircle className="w-6 h-6 text-emerald-600" />
              </div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1.5">Email verified</h1>
              <p className="text-stone-500 text-sm">Taking you to your account...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="inline-flex items-center justify-center mb-4 w-12 h-12 bg-red-100 rounded-xl">
                <FiXCircle className="w-6 h-6 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1.5">Verification failed</h1>
              <p className="text-stone-500 text-sm mb-6">{error}</p>
              <Link
                href="/auth/login"
                className="inline-flex items-center gap-1.5 text-indigo-600 font-semibold hover:text-indigo-700 transition-colors text-sm"
              >
                <FiArrowLeft className="w-3.5 h-3.5" />
                Back to login
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}