import Link from 'next/link';
import { PageHeader } from '@/components/ui/PageHeader';

const values = [
  { title: 'ข้อมูลต้องตรวจสอบได้', text: 'เรามาำให้ทุกผลลัพธ์เชื่อมกลับไปยังแหล่งที่มา และวัดคุณภาพได้อย่างต่อเนื่อง' },
  { title: 'ความปลอดภัยต้องมาแต่แรก', text: 'สิทธิ์ ความเป็นส่วนตัว และ auditability ถูกออกแบบในทุกระดับ ไม่ใช่สิ่งที่เติมตามท้าย' },
  { title: 'เทคโนโลยีต้องสร้างมูลค่า', text: 'เราเลือกสถาปัตยกรรมจากโจทย์จริง และส่งต่อความรู้ให้ทีมใช้งานต่อได้' },
];

export default function AboutPage() {
  return (
    <>
      <section className="bg-white">
        <div className="mx-auto max-w-8xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="max-w-4xl">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">About Knowledge Platform</p>
            <h1 className="mt-4 text-4xl font-bold leading-tight tracking-tight text-gray-900 sm:text-6xl">เราสร้างพื้นฐานให้ความรู้ทำงานได้จริง</h1>
            <p className="mt-6 max-w-2xl text-xl leading-8 text-gray-600">Knowledge Platform รวมนักวิศวกรรมข้อมูล นักวิจัย และผู้เชี่ยวชาญระบบองค์กร เพื่อเปลี่ยนข้อมูลที่กระจัดกระจายให้เป็นระบบที่ปลอดภัย ตรวจสอบได้ และสร้างมูลค่า</p>
          </div>
          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {values.map((item) => (
              <article key={item.title} className="rounded-2xl bg-gray-50 p-7">
                <p className="text-sm font-black text-primary-700">0{values.indexOf(item) + 1}</p>
                <h2 className="mt-5 text-lg font-bold text-gray-900">{item.title}</h2>
                <p className="mt-3 text-sm leading-6 text-gray-600">{item.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="bg-gray-950 py-20 text-white sm:py-24">
        <div className="mx-auto grid max-w-8xl gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-400">Our Mission</p>
            <h2 className="mt-4 text-3xl font-bold sm:text-4xl">ทำให้ AI ให้คำตอบที่องค์กรไว้วางใจได้</h2>
          </div>
          <div className="space-y-6 text-gray-300">
            <p>ระบบ AI ที่มีประโยชน์ไม่ได้เริ่มที่โมเดล แต่เริ่มที่ข้อมูล ที่มา บริบท และกฎการเข้าถึง เราจึงสร้างเครื่องมือที่เชื่อมสิ่งเหล่านั้นเข้าด้วยกัน</p>
            <p>ทีมของเราทำงานแบบ open standards และ API-first เพื่อให้ทุกองค์กรเลือกสิ่งที่เหมาะ กับตัวตนและพัฒนาต่อได้โดยไม่ติดอยู่กับผู้ให้บริการรายใดรายหนึ่ง</p>
            <Link href="/contact" className="inline-flex rounded-lg bg-primary-500 px-5 py-3 text-sm font-bold text-white hover:bg-primary-400">ติดต่อทีมของเรา</Link>
          </div>
        </div>
      </section>
    </>
  );
}
