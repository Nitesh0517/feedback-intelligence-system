import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Unauthorized() {
  const { user } = useAuth();

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-600 mb-6 shadow-sm">
        <ShieldAlert className="w-8 h-8" />
      </div>
      <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Access Denied</h1>
      <p className="mt-2 text-sm text-slate-600 max-w-md">
        Your account role ({user?.role ? <span className="font-semibold capitalize text-slate-800">{user.role}</span> : 'Guest'}) does not have permission to access this resource or execute this operation.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    </div>
  );
}
