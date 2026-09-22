export function LoadingState({ label = 'กำลังโหลดข้อมูล' }: { label?: string }) {
  return (
    <div className="flex min-h-[32rem] items-center justify-center px-6" role="status">
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-700" />
        <p className="text-sm font-medium text-gray-600">{label}</p>
      </div>
    </div>
  );
}

export function ErrorState({
  title = 'ไม่สามารถโหลดข้อมูลได้',
  message,
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex min-h-[24rem] items-center justify-center px-6" role="alert">
      <div className="w-full max-w-md rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
        <div className="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-red-100 text-red-700">
          <span className="text-xl font-bold">!</span>
        </div>
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        {message && <p className="mt-2 whitespace-pre-line text-sm text-gray-600">{message}</p>}
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-5 rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            ลองอีกครั้ง
          </button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({
  title,
  message,
  action,
}: {
  title: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex min-h-[16rem] flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
      <p className="text-lg font-semibold text-gray-900">{title}</p>
      <p className="mt-2 max-w-md text-sm text-gray-600">{message}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function ForbiddenState() {
  return (
    <div className="flex min-h-[36rem] items-center justify-center px-6">
      <div className="w-full max-w-lg text-center">
        <p className="text-sm font-bold uppercase tracking-[0.25em] text-primary-700">403</p>
        <h1 className="mt-3 text-3xl font-bold text-gray-900 sm:text-4xl">คุณไม่มีสิทธิ์เข้าถึงหน้านี้</h1>
        <p className="mt-4 text-gray-600">หน้านี้จำเป็นต้องใช้บัญชีที่มีบทบาทผู้ดูแลระบบ</p>
        <a
          href="/dashboard"
          className="mt-7 inline-flex rounded-lg bg-primary-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          กลับสู่แดชบอร์ด
        </a>
      </div>
    </div>
  );
}
