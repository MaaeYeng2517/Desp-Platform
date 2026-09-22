import './globals.css';
import type { Metadata } from 'next';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { SiteFooter } from '@/components/layout/SiteFooter';
import { SiteHeader } from '@/components/layout/SiteHeader';

export const metadata: Metadata = {
  title: {
    default: 'Knowledge Platform',
    template: '%s | Knowledge Platform',
  },
  description: 'แพลตฟอร์มจัดการความรู้ สืบค้น และสร้างระบบข้อมูลเชิงความรู้ด้วย AI',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body>
        <AuthProvider>
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-white focus:px-4 focus:py-3 focus:shadow-xl"
          >
            ข้ามไปยังเนื้อหาหลัก
          </a>
          <SiteHeader />
          <main id="main-content">{children}</main>
          <SiteFooter />
        </AuthProvider>
      </body>
    </html>
  );
}
