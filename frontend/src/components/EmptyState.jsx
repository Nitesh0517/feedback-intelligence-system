import React from 'react';
import { Inbox, PlusCircle } from 'lucide-react';

export function EmptyState({
  title = 'No feedback found',
  description = 'No feedback entries match your current filter or no feedback has been submitted yet.',
  actionLabel,
  onAction,
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white border border-dashed border-slate-300 rounded-2xl shadow-xs">
      <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-4">
        <Inbox className="w-7 h-7" />
      </div>
      <h3 className="text-base font-semibold text-slate-800">{title}</h3>
      <p className="mt-1.5 text-sm text-slate-500 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-5 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 transition shadow-sm"
        >
          <PlusCircle className="w-4 h-4" />
          {actionLabel}
        </button>
      )}
    </div>
  );
}
