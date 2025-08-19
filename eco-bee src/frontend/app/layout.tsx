import './globals.css';
import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';

const font = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '600', '800'],
  variable: '--font-sans'
});

export const metadata: Metadata = {
  title: 'EcoBee — Your Sustainability Coach',
  description: 'AI-powered sustainability assistant for campus life',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${font.variable} font-sans antialiased bg-app text-app-fore page-stable`}>
        {/* Background: radial glows + grid + noise */}
        <div aria-hidden className="app-backdrop">
          <div className="app-radial app-radial--gold" />
          <div className="app-radial app-radial--teal" />
          <div className="app-grid" />
          <div className="app-noise" />
        </div>
        {children}
      </body>
    </html>
  )
}
