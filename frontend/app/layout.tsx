import type { Metadata } from 'next'
import './styles/globals.css'

export const metadata: Metadata = {
  title: 'AI Agent - Document Analysis',
  description: 'Analyze documents with AI Agent',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body className="bg-white text-gray-900">
        {children}
      </body>
    </html>
  )
}