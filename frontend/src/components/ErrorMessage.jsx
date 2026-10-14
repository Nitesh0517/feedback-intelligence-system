import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded-xl border border-rose-200 bg-rose-50/70 p-5 text-rose-800 shadow-sm">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-rose-600 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-rose-900">Something went wrong</h4>
          <p className="mt-1 text-sm text-rose-700">{message || 'An unexpected error occurred while communicating with the server.'}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-600 text-white hover:bg-rose-700 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
