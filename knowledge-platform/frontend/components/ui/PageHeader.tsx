interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export function PageHeader({ eyebrow, title, description, action, className = '' }: PageHeaderProps) {
  return (
    <div className={`flex flex-col justify-between gap-5 sm:flex-row sm:items-end ${className}`}>
      <div>
        {eyebrow && <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary-700">{eyebrow}</p>}
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{title}</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-gray-600 sm:text-lg">{description}</p>
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
