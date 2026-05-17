import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useAuthStore } from "../store/authStore";
import type { Professional, Community } from "../types";

interface Assignment {
  assignment_id: string;
  professional_display_name: string;
  professional_tier: string;
  community_name: string;
  community_slug: string;
  assigned_at: string;
}

export default function Admin() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [pending, setPending] = useState<Professional[]>([]);
  const [communities, setCommunities] = useState<Community[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [approved, setApproved] = useState<Professional[]>([]);
  const [loading, setLoading] = useState(true);
  const [newCommunity, setNewCommunity] = useState({ name: "", slug: "", addiction_type: "ALCOHOL", description: "" });
  const [assignForm, setAssignForm] = useState({ professional_id: "", community_id: "" });
  const [statusMsg, setStatusMsg] = useState("");

  useEffect(() => {
    if (!user || user.role !== "ADMIN") { navigate("/dashboard"); return; }
    loadAll();
  }, [user]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [pendingRes, commRes, assignRes, approvedRes] = await Promise.all([
        client.get("/admin/professionals/pending"),
        client.get("/admin/communities"),
        client.get("/admin/assignments"),
        client.get("/professionals"),
      ]);
      setPending(pendingRes.data);
      setCommunities(commRes.data);
      setAssignments(assignRes.data);
      setApproved(approvedRes.data);
    } finally {
      setLoading(false);
    }
  };

  const vet = async (id: string, status: "APPROVED" | "REJECTED") => {
    await client.put(`/admin/professionals/${id}/vet`, { status });
    setStatusMsg(`Professional ${status.toLowerCase()}.`);
    loadAll();
  };

  const createCommunity = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/admin/communities", newCommunity);
      setStatusMsg("Community created.");
      setNewCommunity({ name: "", slug: "", addiction_type: "ALCOHOL", description: "" });
      loadAll();
    } catch (err: any) {
      setStatusMsg(err.response?.data?.detail ?? "Error creating community.");
    }
  };

  const assignProfessional = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await client.post("/admin/assign", {
        professional_id: assignForm.professional_id,
        community_id: assignForm.community_id,
      });
      setStatusMsg("Professional assigned.");
      setAssignForm({ professional_id: "", community_id: "" });
      loadAll();
    } catch (err: any) {
      setStatusMsg(err.response?.data?.detail ?? "Assignment failed.");
    }
  };

  const ADDICTION_TYPES = ["ALCOHOL","DRUGS","GAMBLING","GAMING","SEX","FOOD","SMOKING","OTHER"];

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>

      {statusMsg && (
        <div className="bg-green-50 text-green-700 text-sm rounded-lg px-4 py-2 mb-4 flex justify-between">
          {statusMsg}
          <button onClick={() => setStatusMsg("")} className="text-green-500 font-bold">×</button>
        </div>
      )}

      {loading ? (
        <div className="text-gray-400">Loading...</div>
      ) : (
        <div className="space-y-10">

          {/* Pending Professionals */}
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              Pending Vetting <span className="text-sm bg-yellow-100 text-yellow-700 rounded-full px-2 py-0.5">{pending.length}</span>
            </h2>
            {pending.length === 0 ? (
              <p className="text-sm text-gray-400">No pending applications.</p>
            ) : (
              <div className="space-y-3">
                {pending.map((p) => (
                  <div key={p.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-start justify-between gap-4">
                    <div className="text-sm">
                      <p className="font-semibold text-gray-900">{p.display_name}</p>
                      <p className="text-gray-500">{p.specialty} · {p.tier} Tier · {p.years_experience} yrs exp</p>
                      {p.bio && <p className="text-gray-500 mt-1 line-clamp-2">{p.bio}</p>}
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button onClick={() => vet(p.id, "APPROVED")}
                        className="bg-green-600 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-green-700 transition">
                        Approve
                      </button>
                      <button onClick={() => vet(p.id, "REJECTED")}
                        className="bg-red-100 text-red-600 text-xs px-3 py-1.5 rounded-lg hover:bg-red-200 transition">
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Assign Professional */}
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Assign Professional to Community</h2>
            <form onSubmit={assignProfessional} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-[180px]">
                <label className="block text-xs font-semibold text-gray-600 mb-1">Professional</label>
                <select value={assignForm.professional_id} onChange={(e) => setAssignForm(f => ({...f, professional_id: e.target.value}))} required
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                  <option value="">Select...</option>
                  {approved.map((p) => (
                    <option key={p.id} value={p.id}>{p.display_name} ({p.tier})</option>
                  ))}
                </select>
              </div>
              <div className="flex-1 min-w-[180px]">
                <label className="block text-xs font-semibold text-gray-600 mb-1">Community</label>
                <select value={assignForm.community_id} onChange={(e) => setAssignForm(f => ({...f, community_id: e.target.value}))} required
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                  <option value="">Select...</option>
                  {communities.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}{c.required_tier ? ` (${c.required_tier})` : ""}</option>
                  ))}
                </select>
              </div>
              <button type="submit" className="bg-brand-600 text-white text-sm px-4 py-2 rounded-xl hover:bg-brand-700 transition">
                Assign
              </button>
            </form>
          </section>

          {/* Active Assignments */}
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Active Assignments</h2>
            {assignments.length === 0 ? (
              <p className="text-sm text-gray-400">No active assignments.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 text-xs uppercase tracking-wider border-b">
                      <th className="pb-2 pr-4">Professional</th>
                      <th className="pb-2 pr-4">Tier</th>
                      <th className="pb-2 pr-4">Community</th>
                      <th className="pb-2">Assigned</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {assignments.map((a) => (
                      <tr key={a.assignment_id}>
                        <td className="py-2 pr-4 font-medium text-gray-900">{a.professional_display_name}</td>
                        <td className="py-2 pr-4"><span className="bg-brand-100 text-brand-700 text-xs px-2 py-0.5 rounded-full">{a.professional_tier}</span></td>
                        <td className="py-2 pr-4 text-gray-600">{a.community_name}</td>
                        <td className="py-2 text-gray-400">{new Date(a.assigned_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Create Community */}
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Create Community</h2>
            <form onSubmit={createCommunity} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 space-y-3">
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Name</label>
                  <input value={newCommunity.name} onChange={(e) => setNewCommunity(f => ({...f, name: e.target.value}))} required
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                </div>
                <div className="flex-1">
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Slug</label>
                  <input value={newCommunity.slug} onChange={(e) => setNewCommunity(f => ({...f, slug: e.target.value}))} required
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Type</label>
                  <select value={newCommunity.addiction_type} onChange={(e) => setNewCommunity(f => ({...f, addiction_type: e.target.value}))}
                    className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                    {ADDICTION_TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Description</label>
                <input value={newCommunity.description} onChange={(e) => setNewCommunity(f => ({...f, description: e.target.value}))}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <button type="submit" className="bg-gray-900 text-white text-sm px-4 py-2 rounded-xl hover:bg-gray-700 transition">
                Create community
              </button>
            </form>
          </section>

        </div>
      )}
    </div>
  );
}
