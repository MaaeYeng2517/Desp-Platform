import Link from 'next/link';
import { PageHeader } from '@/components/ui/PageHeader';

const articles = [
  {
    category: 'RAG Architecture',
    title: 'ออกแบบ Retrieval Pipeline ที่ตรวจสอบคำตอบได้',
    summary: 'เรียนรู้วิธีเชื่อมโยง chunk, metadata และ citation เพื่อให้ทุกคำตอบมีแหล่งที่มาและวัดความถูกต้องได้',
    date: '22 กันยายน 2026',
  },
  {
    category: 'Knowledge Governance',
    title: 'RBAC และ Multi-tenancy สำหรับแพลตฟอร์มความรู้',
    summary: 'แนวทางออกแบบสิทธิ์และการแยกข้อมูลตั้งแต่ระดับ API ไปจนถึงแหล่งข้อมูลและผลลัพธ์การค้นหา',
    date: '15 กันยายน 2026',
  },
  {
    category: 'Evaluation',
    title: 'วัดคุณภาพ RAG ก่อนนำขึ้นผลิตจริง',
    summary: 'ใช้ dataset, relevance metrics และ human review เพื่อจับความล้มเหลวที่ latency หรือ demo ไม่สามารถแสดงได้',
    date: '8 กันยายน 2026',
  },
];

export default function ArticlesPage() {
  return (
    <div className="bg-gray-50 py-12 sm:py-16">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <PageHeader eyebrow="Insights" title="บทความและแนวทางปฏิบัติ" description="ความรู้เชิงลึกด้าน knowledge engineering, retrieval, evaluation และ governance" />
        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          {articles.map((article) => (
            <article key={article.title} className="flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-6 transition hover:-translate-y-1 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-primary-700">{article.category}</span>
                <time className="text-gray-500">{article.date}</time>
              </div>
              <h2 className="mt-5 text-xl font-bold leading-8 text-gray-900">{article.title}</h2>
              <p className="mt-3 flex-1 text-sm leading-6 text-gray-600">{article.summary}</p>
              <Link href="/contact?subject=บทความ" className="mt-6 inline-flex items-center gap-2 text-sm font-bold text-primary-700 hover:text-primary-800">
                อ่านบทความ <span aria-hidden="true">→</span>
              </Link>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
