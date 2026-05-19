import type { LucideIcon } from "lucide-react";

type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  tone?: "neutral" | "success" | "warning" | "danger";
};

const toneClasses = {
  neutral: "text-blue-700 bg-blue-50 border-blue-100",
  success: "text-emerald-700 bg-emerald-50 border-emerald-100",
  warning: "text-amber-700 bg-amber-50 border-amber-100",
  danger: "text-red-700 bg-red-50 border-red-100",
};

export function MetricCard({ label, value, detail, icon: Icon, tone = "neutral" }: MetricCardProps) {
  return (
    <section className="rounded-lg border border-[var(--border)] bg-[var(--panel)] p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-[var(--muted)]">{label}</p>
          <p className="mt-2 text-2xl font-semibold tracking-normal text-[var(--foreground)]">{value}</p>
        </div>
        <div className={`rounded-md border p-2 ${toneClasses[tone]}`}>
          <Icon aria-hidden="true" size={18} />
        </div>
      </div>
      <p className="mt-3 text-sm text-[var(--muted)]">{detail}</p>
    </section>
  );
}
