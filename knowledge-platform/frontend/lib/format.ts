export function formatDateTime(value: string | null | undefined): string {
  if (!value) return 'ไม่มีข้อมูล';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('th-TH', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return 'ไม่มีข้อมูล';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('th-TH', { dateStyle: 'long' }).format(date);
}

export function formatMoney(cents: number, currency: string): string {
  try {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: currency.toUpperCase(),
      maximumFractionDigits: 0,
    }).format(cents / 100);
  } catch {
    return `${(cents / 100).toLocaleString('th-TH')} ${currency.toUpperCase()}`;
  }
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('th-TH').format(value);
}
