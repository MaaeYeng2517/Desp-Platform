import Link from 'next/link';

export function SiteFooter() {
  return (
    <footer className="border-t border-gray-200 bg-gray-950 text-gray-300">
      <div className="mx-auto grid max-w-8xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1.4fr_1fr_1fr] lg:px-8">
        <div>
          <p className="text-base font-bold text-white">Knowledge Platform</p>
          <p className="mt-3 max-w-md text-sm leading-6 text-gray-400">
            แพลตฟอร์มกลางสำหรับสร้าง จัดการ และให้บริการความรู้ในองค์กรอย่างปลอดภัย
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold text-white">แพลตฟอร์ม</p>
          <ul className="mt-4 space-y-2 text-sm">
            <li><Link href="/products" className="hover:text-white">สินค้าและแผน</Link></li>
            <li><Link href="/services" className="hover:text-white">บริการ</Link></li>
            <li><Link href="/articles" className="hover:text-white">บทความ</Link></li>
          </ul>
        </div>
        <div>
          <p className="text-sm font-semibold text-white">บริษัท</p>
          <ul className="mt-4 space-y-2 text-sm">
            <li><Link href="/about" className="hover:text-white">เกี่ยวกับเรา</Link></li>
            <li><Link href="/contact" className="hover:text-white">ติดต่อเรา</Link></li>
            <li><Link href="/auth/login" className="hover:text-white">เข้าสู่ระบบ</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-800">
        <p className="mx-auto max-w-8xl px-4 py-5 text-xs text-gray-500 sm:px-6 lg:px-8">
          © {new Date().getFullYear()} Knowledge Engineering Platform
        </p>
      </div>
    </footer>
  );
}
