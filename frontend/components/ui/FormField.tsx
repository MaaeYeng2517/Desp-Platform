interface FieldProps {
  label: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}

export function Field({ label, error, hint, children }: FieldProps) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-3">
        <label className="text-sm font-semibold text-gray-800">{label}</label>
        {hint && !error && <span className="text-xs text-gray-500">{hint}</span>}
      </div>
      {children}
      {error ? (
        <p role="alert" className="mt-1.5 text-xs font-medium text-red-700">{error}</p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-gray-500">{hint}</p>
      ) : null}
    </div>
  );
}

export function inputClassName(error?: string): string {
  return `mt-0 block w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-4 ${
    error
      ? 'border-red-300 focus:border-red-500 focus:ring-red-100'
      : 'border-gray-300 focus:border-primary-600 focus:ring-primary-100'
  }`;
}
