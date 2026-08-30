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
      <body>
        {children}
      </body>
    </html>
  )
}