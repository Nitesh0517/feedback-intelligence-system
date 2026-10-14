import React, { useState, useEffect } from 'react';
import { Users as UsersIcon, Shield, CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { userApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { LoadingSpinner } from '../components/LoadingSpinner';

export function Users() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');

  const { user: currentAdmin } = useAuth();

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await userApi.list({ skip: 0, limit: 50 });
      setUsers(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.message || 'Failed to fetch user list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    setError('');
    setActionMessage('');
    try {
      await userApi.updateRole(userId, newRole);
      setActionMessage(`Role updated successfully to ${newRole}`);
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to update user role.');
    }
  };

  const handleStatusToggle = async (userId, currentStatus) => {
    setError('');
    setActionMessage('');
    try {
      await userApi.updateStatus(userId, !currentStatus);
      setActionMessage(`User account ${!currentStatus ? 'activated' : 'deactivated'} successfully.`);
      fetchUsers();
    } catch (err) {
      setError(err.message || 'Failed to update account status.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            <UsersIcon className="w-6 h-6 text-indigo-600" />
            <span>User Management</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Administrator directory of system accounts, operational roles, and access controls.
          </p>
        </div>
        <button
          onClick={fetchUsers}
          className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 shadow-sm transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center">
            <LoadingSpinner text="Loading user directory..." />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Role</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {users.map((u) => {
                  const isSelf = u.id === currentAdmin?.id;
                  return (
                    <tr key={u.id} className="hover:bg-slate-50/60 transition">
                      <td className="py-3.5 px-4 font-medium text-slate-900">
                        <div className="flex items-center gap-2">
                          <span>{u.name}</span>
                          {isSelf && (
                            <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                              You
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">{u.email}</td>
                      <td className="py-3.5 px-4">
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="text-xs font-semibold px-2.5 py-1 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 capitalize"
                        >
                          <option value="admin">Admin</option>
                          <option value="analyst">Analyst</option>
                          <option value="viewer">Viewer</option>
                        </select>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                            u.is_active
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {u.is_active ? (
                            <>
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              Active
                            </>
                          ) : (
                            <>
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                              Deactivated
                            </>
                          )}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => handleStatusToggle(u.id, u.is_active)}
                          disabled={isSelf}
                          className={`text-xs font-semibold px-3 py-1 rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed ${
                            u.is_active
                              ? 'text-rose-700 hover:bg-rose-50 border border-rose-200'
                              : 'text-emerald-700 hover:bg-emerald-50 border border-emerald-200'
                          }`}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
