'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FiMail, FiLock, FiArrowLeft, FiCheck, FiLoader, FiAlertCircle } from 'react-icons/fi'

type ForgotPasswordStep = 'email' | 'code' | 'reset'

interface ResetFormData {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
}

export default function ForgotPasswordPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState<ForgotPasswordStep>('email')
  const [formData, setFormData] = useState<ResetFormData>({
    email: '',
    code: '',
    newPassword: '',
    confirmPassword: '',
  })

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Step 1: Request Password Reset
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    // Validation
    if (!formData.email.includes('@')) {
      setError('Veuillez entrer une adresse email valide')
      setIsLoading(false)
      return
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Move to next step
      setCurrentStep('code')
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError('Une erreur est survenue. Veuillez réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  // Step 2: Verify Reset Code
  const handleCodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    // Validation
    if (formData.code.length < 6) {
      setError('Le code doit contenir au moins 6 caractères')
      setIsLoading(false)
      return
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Move to next step
      setCurrentStep('reset')
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError('Code invalide. Veuillez vérifier et réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  // Step 3: Reset Password
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    // Validation
    if (formData.newPassword.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
      setIsLoading(false)
      return
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      setIsLoading(false)
      return
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Success - redirect to login
      setSuccess(true)
      setTimeout(() => {
        router.push('/auth/login')
      }, 2000)
    } catch (err) {
      setError('Une erreur est survenue. Veuillez réessayer.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
        {/* Back Button */}
        <Link
          href="/auth/login"
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold mb-6 transition-colors"
        >
          <FiArrowLeft className="w-5 h-5" />
          Retour
        </Link>

        {/* Progress Indicator */}
        <div className="flex gap-2 mb-8">
          <div className={`h-1 flex-1 rounded-full ${currentStep === 'email' || currentStep === 'code' || currentStep === 'reset' ? 'bg-blue-600' : 'bg-gray-300'}`} />
          <div className={`h-1 flex-1 rounded-full ${currentStep === 'code' || currentStep === 'reset' ? 'bg-blue-600' : 'bg-gray-300'}`} />
          <div className={`h-1 flex-1 rounded-full ${currentStep === 'reset' ? 'bg-blue-600' : 'bg-gray-300'}`} />
        </div>

        {/* Step 1: Email Verification */}
        {currentStep === 'email' && (
          <div>
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Réinitialiser Votre Mot de Passe</h1>
              <p className="text-gray-600">Entrez votre adresse email pour recevoir un code de réinitialisation</p>
            </div>

            {success && (
              <div className="flex items-center gap-3 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
                <FiCheck className="w-5 h-5" />
                <span>Un email a été envoyé à {formData.email}</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                <FiAlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleEmailSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse Email
                </label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-3.5 text-gray-400 w-5 h-5" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="vous@example.com"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <FiLoader className="animate-spin" />
                    Envoi en cours...
                  </>
                ) : (
                  'Envoyer le Code'
                )}
              </button>

              <div className="text-center">
                <p className="text-gray-600 text-sm">
                  Vous souvenez-vous de votre mot de passe?{' '}
                  <Link href="/auth/login" className="text-blue-600 hover:text-blue-700 font-semibold">
                    Connectez-vous
                  </Link>
                </p>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Code Verification */}
        {currentStep === 'code' && (
          <div>
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Entrez le Code</h1>
              <p className="text-gray-600">Nous avons envoyé un code à {formData.email}</p>
            </div>

            {success && (
              <div className="flex items-center gap-3 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
                <FiCheck className="w-5 h-5" />
                <span>Code vérifié avec succès</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                <FiAlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleCodeSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code de Réinitialisation
                </label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="000000"
                  maxLength={6}
                  required
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-center text-2xl tracking-widest font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-600 mt-2">Le code est valide pendant 10 minutes</p>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <FiLoader className="animate-spin" />
                    Vérification...
                  </>
                ) : (
                  'Vérifier le Code'
                )}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setCurrentStep('email')
                    setError('')
                  }}
                  className="text-blue-600 hover:text-blue-700 font-semibold text-sm"
                >
                  Utiliser une autre adresse email
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 3: New Password */}
        {currentStep === 'reset' && (
          <div>
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Créer un Nouveau Mot de Passe</h1>
              <p className="text-gray-600">Entrez un mot de passe fort et sécurisé</p>
            </div>

            {success && (
              <div className="flex items-center gap-3 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
                <FiCheck className="w-5 h-5" />
                <span>Mot de passe réinitialisé. Redirection...</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                <FiAlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handlePasswordSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nouveau Mot de Passe
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-3.5 text-gray-400 w-5 h-5" />
                  <input
                    type="password"
                    value={formData.newPassword}
                    onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                    placeholder="••••••••"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <p className="text-xs text-gray-600 mt-2">Au moins 8 caractères avec majuscules, minuscules et chiffres</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmer le Mot de Passe
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-3.5 text-gray-400 w-5 h-5" />
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    placeholder="••••••••"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Password Requirements */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-xs font-semibold text-gray-700 mb-2">Exigences du Mot de Passe :</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li className={formData.newPassword.length >= 8 ? 'text-green-600' : ''}>
                    ✓ Au moins 8 caractères
                  </li>
                  <li className={/[A-Z]/.test(formData.newPassword) ? 'text-green-600' : ''}>
                    ✓ Au moins une lettre majuscule
                  </li>
                  <li className={/[a-z]/.test(formData.newPassword) ? 'text-green-600' : ''}>
                    ✓ Au moins une lettre minuscule
                  </li>
                  <li className={/[0-9]/.test(formData.newPassword) ? 'text-green-600' : ''}>
                    ✓ Au moins un chiffre
                  </li>
                </ul>
              </div>

              <button
                type="submit"
                disabled={isLoading || formData.newPassword.length < 8}
                className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <FiLoader className="animate-spin" />
                    Réinitialisation en cours...
                  </>
                ) : (
                  'Réinitialiser le Mot de Passe'
                )}
              </button>
            </form>
          </div>
        )}

        {/* Security Info */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-xs text-gray-600 text-center">
            🔒 Vos données sont sécurisées et chiffrées. Nous ne partageons jamais vos informations personnelles.
          </p>
        </div>
      </div>
    </div>
  )
}