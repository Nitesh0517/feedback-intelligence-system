import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  PlusCircle,
  TrendingUp,
  Activity,
  Menu,
  X,
  Sparkles,
  LogOut,
  Users as UsersIcon,
  Shield,
} from 'lucide-react';
import { healthApi } from '../services/api';
import { useAuth } from '../context/AuthContext';

export function DashboardLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', db: 'checking' });

  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    const checkStatus = async () => {
      try {
        const res = await healthApi.checkReady();
        if (isMounted) {
          setSystemHealth({
            status: res.status === 'ready' ? 'online' : 'degraded',
            db: res.database,
          });
        }
      } catch (err) {
        if (isMounted) {
          setSystemHealth({ status: 'offline', db: 'unreachable' });
        }
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Role-aware navigation definitions
  const allNavItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard, roles: ['admin', 'analyst', 'viewer'] },
    { to: '/feedback', label: 'Feedback Feed', icon: MessageSquare, roles: ['admin', 'analyst', 'viewer'] },
    { to: '/submit', label: 'Submit Feedback', icon: PlusCircle, roles: ['admin', 'analyst'] },
    { to: '/analytics', label: 'Analytics & Trends', icon: TrendingUp, roles: ['admin', 'analyst', 'viewer'] },
    { to: '/users', label: 'User Management', icon: UsersIcon, roles: ['admin'] },
  ];

  const visibleNavItems = allNavItems.filter((item) =>
    item.roles.some((r) => hasRole(r))
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row">
      {/* Mobile top bar */}
      <div className="md:hidden flex items-center justify-between bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="font-bold text-slate-800 text-sm tracking-tight">Feedback Intelligence</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg text-slate-600 hover:bg-slate-100"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-slate-900 text-slate-300 transform transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:inset-auto md:min-h-screen flex flex-col ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-0 -translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white tracking-tight leading-none">Feedback Intelligence</h1>
              <p className="text-xs text-slate-400 mt-1">AI Analytics Platform</p>
            </div>
          </div>
        </div>

        {/* User Profile Pill in Sidebar */}
        {user && (
          <div className="px-4 py-3 mx-4 mt-4 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
            <div className="min-w-0 pr-2">
              <p className="text-xs font-semibold text-white truncate">{user.name}</p>
              <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
            </div>
            <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {user.role}
            </span>
          </div>
        )}

        {/* Links */}
        <nav className="flex-1 p-4 space-y-1">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Logout and Health Status Footer */}
        <div className="p-4 border-t border-slate-800 space-y-3">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-slate-400" />
              <div className="text-xs">
                <p className="font-medium text-slate-300">API Status</p>
                <p className="text-[10px] text-slate-400 capitalize">DB: {systemHealth.db}</p>
              </div>
            </div>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium ${
                systemHealth.status === 'online'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : systemHealth.status === 'checking'
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'bg-rose-500/20 text-rose-400'
              }`}
            >
              {systemHealth.status}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
