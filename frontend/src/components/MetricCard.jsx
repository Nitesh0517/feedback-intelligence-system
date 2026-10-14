import React from 'react';

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
  loading = false,
}) {
  const variantStyles = {
    default: {
      card: 'border-slate-200',
      iconBg: 'bg-slate-100 text-slate-700',
      valueText: 'text-slate-900',
    },
    positive: {
      card: 'border-emerald-200 bg-emerald-50/20',
      iconBg: 'bg-emerald-100 text-emerald-700',
      valueText: 'text-emerald-700',
    },
    negative: {
      card: 'border-rose-200 bg-rose-50/20',
      iconBg: 'bg-rose-100 text-rose-700',
      valueText: 'text-rose-700',
    },
    neutral: {
      card: 'border-slate-200 bg-slate-50/30',
      iconBg: 'bg-slate-100 text-slate-600',
      valueText: 'text-slate-700',
    },
    indigo: {
      card: 'border-indigo-200 bg-indigo-50/20',
      iconBg: 'bg-indigo-100 text-indigo-700',
      valueText: 'text-indigo-700',
    },
    amber: {
      card: 'border-amber-200 bg-amber-50/20',
      iconBg: 'bg-amber-100 text-amber-700',
      valueText: 'text-amber-700',
    },
  };

  const style = variantStyles[variant] || variantStyles.default;

  return (
    <div
      data-testid="metric-card"
      className={`bg-white p-5 rounded-2xl border ${style.card} shadow-xs flex items-center justify-between transition hover:shadow-sm`}
    >
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </p>
        {loading ? (
          <div className="h-8 w-16 bg-slate-200 animate-pulse rounded-md mt-1" />
        ) : (
          <p className={`text-2xl font-bold tracking-tight ${style.valueText}`}>
            {value !== undefined && value !== null ? value : 0}
          </p>
        )}
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      {Icon && (
        <div
          className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${style.iconBg}`}
        >
          <Icon className="w-6 h-6" />
        </div>
      )}
    </div>
  );
}
