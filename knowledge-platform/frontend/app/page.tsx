'use client';

import Link from 'next/link';

const capabilities = [
  {
    title: 'เชื่อมต่อแหล่งข้อมูล',
    description: 'นำเข้าเอกสาร เว็บไซต์ ฐานข้อมูล และ API ผ่านโครงสร้างตัวเชื่อมต่อที่ขยายได้',
    detail: 'Multi-source ingestion',
  },
  {
    title: 'จัดการความรู้',
    description: 'จัดการวงจรชีพของเอกสาร การแยกข้อความ ชิงก์ และเมตาดาทาในพื้นที่ทำงานเดียว',
    detail: 'Knowledge operations',
  },
  {
    title: 'ค้นหาแบบไฮบริด',
    description: 'ผสาน Keyword, Vector, Metadata และ Graph Search เพื่อความแม่นยำที่ตรวจสอบได้',
    detail: 'Hybrid retrieval',
  },
  {
    title: 'RAG ที่ไว้ใจได้',
    description: 'สร้างคำตอบพร้อมบริบท การอ้างอิง และการตรวจสอบข้อมูลจากแหล่งต้นทาง',
    detail: 'Verified RAG',
  },
  {
    title: 'Workflow เชิงภาพ',
    description: 'ออกแบบ ไปป์ไลน์ข้อมูลแบบ end-to-end ด้วยโหนดที่ทำงานได้จริงและติดตามสถานะ',
    detail: 'Visual orchestration',
  },
  {
    title: 'ธรรมาภิบาลและความปลอดภัย',
    description: 'RBAC, Multi-tenancy, Audit Log และ API Governance ในทุกระดับการเข้าถึง',
    detail: 'Enterprise governance',
  },
];

export default function Home() {
  return (
    <>
      <section className="overflow-hidden bg-gray-950 text-white">
        <div className="absolute inset-0 opacity-20" aria-hidden="true">
          <div className="absolute -left-24 top-0 h-96 w-96 rounded-full bg-primary-600 blur-3xl" />
          <div className="absolute right-0 top-40 h-80 w-80 rounded-full bg-primary-400 blur-3xl" />
        </div>
        <div className="relative mx-auto grid max-w-8xl items-center gap-12 px-4 py-20 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:py-28">
          <div>
            <p className="inline-flex rounded-full border border-primary-400/30 bg-primary-400/10 px-3 py-1 text-xs font-bold tracking-wide text-primary-200">
              KNOWLEDGE INFRASTRUCTURE
            </p>
            <h1 className="mt-6 text-4xl font-bold leading-[1.15] tracking-tight sm:text-6xl">
              เปลี่ยนความรู้ที่กระจาย
              <span className="bg-gradient-to-r from-primary-300 to-cyan-300 bg-clip-text text-transparent"> ให้เป็นระบบที่สร้างมูลค่า</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-300">
              แพลตฟอร์มกลางสำหรับจัดการ สืบค้น และให้บริการความรู้ด้วย AI พร้อมระบบปลอดภัยและการเชื่อมต่อ API ที่พร้อมใช้งานในระดับองค์กร
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/products" className="inline-flex justify-center rounded-lg bg-primary-500 px-6 py-3.5 text-sm font-bold text-white transition hover:bg-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-500/30">
                เลือกแผนที่เหมาะกับทีม
              </Link>
              <Link href="/services" className="inline-flex justify-center rounded-lg border border-gray-700 bg-white/5 px-6 py-3.5 text-sm font-bold text-white transition hover:bg-white/10 focus:outline-none focus:ring-4 focus:ring-white/10">
                ดูบริการของเรา
              </Link>
            </div>
            <dl className="mt-12 grid max-w-lg grid-cols-3 gap-6 border-t border-gray-800 pt-7">
              <div>
                <dt className="text-xs text-gray-400">API-first</dt>
                <dd className="mt-1 text-lg font-bold text-white">พร้อมเชื่อมต่อ</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Security</dt>
                <dd className="mt-1 text-lg font-bold text-white">RBAC + CSRF</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-400">Deployment</dt>
                <dd className="mt-1 text-lg font-bold text-white">Private cloud</dd>
              </div>
            </dl>
          </div>
          <div className="relative rounded-2xl border border-gray-800 bg-gray-900/80 p-5 shadow-2xl sm:p-7">
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div>
                <p className="text-xs font-bold text-gray-400">RETRIEVAL PIPELINE</p>
                <p className="mt-1 text-sm font-semibold text-white">Query to verified answer</p>
              </div>
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,0.8)]" aria-hidden="true" />
            </div>
            <ol className="mt-6 space-y-3">
              {['Ingest', 'Chunk', 'Index', 'Retrieve', 'Verify'].map((step, index) => (
                <li key={step} className="flex items-center gap-4">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary-500/15 text-xs font-bold text-primary-300 ring-1 ring-inset ring-primary-400/20">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="h-px flex-1 bg-gray-800" aria-hidden="true" />
                  <span className="w-20 text-right text-sm font-medium text-gray-300">{step}</span>
                </li>
              ))}
            </ol>
            <div className="mt-7 rounded-xl bg-black/30 p-4">
              <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Verified response</p>
              <p className="mt-2 text-sm leading-6 text-gray-200">คำตอบทุกข้อผูกกับแหล่งข้อมูล ติดตามย้อนกลับได้ และตรวจสอบได้</p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white py-20 sm:py-24">
        <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">PLATFORM CAPABILITIES</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">พื้นฐานที่ครบทุกขั้นของงานความรู้</h2>
            <p className="mt-4 text-lg leading-8 text-gray-600">ออกแบบมาเพื่อทีมข้อมูลและองค์กรที่ต้องการความถูกต้อง โปร่งใส และความสามารถในการขยายตัว</p>
          </div>
          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((item) => (
              <article key={item.detail} className="group rounded-2xl border border-gray-200 bg-white p-6 transition hover:-translate-y-1 hover:border-primary-200 hover:shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="h-10 w-10 rounded-xl bg-primary-50 text-primary-700 ring-1 ring-inset ring-primary-100 flex items-center justify-center text-sm font-black">{item.title.charAt(0)}</span>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{item.detail}</span>
                </div>
                <h3 className="mt-6 text-lg font-bold text-gray-900">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">{item.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-gray-50 py-20 sm:py-24">
        <div className="mx-auto grid max-w-8xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div className="rounded-2xl bg-gray-950 p-5 shadow-2xl sm:p-8">
            <div className="space-y-3 font-mono text-xs sm:text-sm">
              <p className="text-gray-500">$ curl api.knowledge-platform/v1/search</p>
              <p className="text-emerald-400">200 OK · 18 ms · 5 cited sources</p>
              <p className="text-gray-300">{"{"} query, context, citations, verification {"}"}</p>
            </div>
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">DEVELOPER READY</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">ปลดล็อกข้อมูลด้วย API ที่ปลอดภัย</h2>
            <p className="mt-4 text-lg leading-8 text-gray-600">จัดการ API Key กำหนดสิทธิ์ต่อ.scope ติดตามการใช้งาน และสร้างผลานงานบนพื้นฐานที่เชื่อมกับระบบเดิมได้</p>
            <ul className="mt-7 space-y-4">
              {['Credential และ CSRF Protection', 'Role-based Access Control', 'Usage Audit และ API Key Lifecycle'].map((item) => (
                <li key={item} className="flex items-center gap-3 text-sm font-medium text-gray-800">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">✓</span>
                  {item}
                </li>
              ))}
            </ul>
            <Link href="/auth/register" className="mt-8 inline-flex rounded-lg bg-primary-700 px-5 py-3 text-sm font-bold text-white hover:bg-primary-800">
              เริ่มสร้าง API Key แรก
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
