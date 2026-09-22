import Link from 'next/link';
import { PageHeader } from '@/components/ui/PageHeader';

const services = [
  {
    title: 'ปรับสถาปัตยกรรมความรู้',
    description: 'วิเคราะห์แหล่งข้อมูล ออกแบบ pipeline และเลือกเทคโนโลยีให้เหมาะสมกับปริมาณและระดับความลับ',
    deliverables: ['Assessment', 'Target architecture', 'Implementation roadmap'],
  },
  {
    title: 'พัฒนา RAG และ AI Agents',
    description: 'สร้างระบบตอบคำถามและเอเจนต์ที่มีการอ้างอิง ตรวจสอบได้ และเชื่อมต่อกับเครื่องมือของทีม',
    deliverables: ['Retrieval design', 'Evaluation suite', 'Production integration'],
  },
  {
    title: 'ยกระดับ Data & Knowledge Governance',
    description: 'กำหนดสิทธิ์ การตรวจสอบ และวงจรชีพข้อมูล เพื่อให้ความรู้ถูกใช้งานอย่างปลอดภัยและรักษาได้',
    deliverables: ['RBAC model', 'Audit controls', 'Operating playbook'],
  },
  {
    title: 'ฝึกอบรมและส่งต่อทีม',
    description: 'พัฒนาทักษะด้าน knowledge engineering ผ่าน workshop และลงมือทำกับ用例จริง',
    deliverables: ['Hands-on workshop', 'Technical enablement', 'Team handover'],
  },
];

export default function ServicesPage() {
  return (
    <>
      <section className="bg-gray-950 text-white">
        <div className="mx-auto max-w-8xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <PageHeader
            eyebrow="Professional Services"
            title="เร่งการส่งมอบด้วยผู้เชี่ยวชาญ"
            description="บริการแบบ end-to-end ตั้งแต่กำหนดยุทธศาสตร์ จนถึงการสร้างและส่งต่อระบบความรู้ที่ทำงานได้จริง"
            action={<Link href="/contact" className="inline-flex rounded-lg bg-primary-500 px-5 py-3 text-sm font-bold text-white hover:bg-primary-400">ปรึกษาโครงการ</Link>}
            className="max-w-4xl"
          />
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {[
              { value: '01', label: 'Discover', text: 'เข้าใจโจทย์ ข้อมูล ผู้ใช้ และข้อจำกัด' },
              { value: '02', label: 'Build', text: 'พัฒนาแบบวนซ้ำ พร้อมวัดผลทุกขั้น' },
              { value: '03', label: 'Operate', text: 'ส่งต่อระบบ เอกสาร และความสามารถให้ทีม' },
            ].map((item) => (
              <div key={item.value} className="rounded-2xl border border-gray-800 bg-white/5 p-6">
                <p className="text-3xl font-black text-primary-400">{item.value}</p>
                <p className="mt-5 text-lg font-bold">{item.label}</p>
                <p className="mt-2 text-sm leading-6 text-gray-400">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="bg-white py-20 sm:py-24">
        <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">Engagement Models</p>
            <h2 className="mt-3 text-3xl font-bold text-gray-900">เลือกการทำงานที่เหมาะกับทีม</h2>
          </div>
          <div className="mt-10 grid gap-6 md:grid-cols-2">
            {services.map((service) => (
              <article key={service.title} className="rounded-2xl border border-gray-200 bg-gray-50 p-7">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-100 font-bold text-primary-800">{service.title.charAt(0)}</span>
                <h3 className="mt-5 text-xl font-bold text-gray-900">{service.title}</h3>
                <p className="mt-3 text-sm leading-6 text-gray-600">{service.description}</p>
                <p className="mt-5 text-xs font-bold uppercase tracking-wider text-gray-500">สิ่งที่ส่งมอบ</p>
                <ul className="mt-3 space-y-2 text-sm text-gray-700">
                  {service.deliverables.map((item) => <li key={item} className="flex gap-2"><span className="text-primary-700">✓</span>{item}</li>)}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
