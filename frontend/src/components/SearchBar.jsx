import React from 'react';
import { Search, X } from 'lucide-react';

export function SearchBar({ value, onChange, onSubmit, placeholder = 'Search customer feedback...' }) {
  const handleClear = () => {
    onChange('');
    if (onSubmit) {
      onSubmit('');
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(value);
    }
  };

  return (
    <form onSubmit={handleFormSubmit} className="flex gap-2 w-full">
      <div className="relative flex-1">
        <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full pl-9 pr-9 py-2 text-sm rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-white"
        />
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
            title="Clear search"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      <button
        type="submit"
        className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition flex-shrink-0"
      >
        Search
      </button>
    </form>
  );
}
