import { useEffect, useState } from "react";
import { getMyGroups, getMyProfessionalProfile } from "../api/professionals";
import { getFeed } from "../api/posts";
import type { Community, Post, Professional } from "../types";

export default function ProfessionalPortal() {
  const [profile, setProfile] = useState<Professional | null>(null);
  const [groups, setGroups] = useState<Community[]>([]);
  const [activeCommunity, setActiveCommunity] = useState<Community | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getMyProfessionalProfile(), getMyGroups()])
      .then(([prof, grps]) => {
        setProfile(prof);
        setGroups(grps);
        if (grps.length > 0) {
          setActiveCommunity(grps[0]);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!activeCommunity) return;
    getFeed(activeCommunity.slug).then((data) => setPosts(data.posts));
  }, [activeCommunity]);

  if (loading) return <div className="p-8 text-gray-400">Loading portal...</div>;
  if (!profile) return <div className="p-8 text-gray-500">No professional profile found.</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 flex gap-6">
      <aside className="w-56 shrink-0">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-1">Your Profile</p>
          <p className="font-bold text-gray-900">{profile.display_name}</p>
          <p className="text-xs text-gray-500 capitalize">{profile.specialty.toLowerCase()}</p>
          <span className={`mt-2 inline-block text-xs px-2 py-0.5 rounded-full font-medium ${
            profile.vetting_status === "APPROVED"
              ? "bg-green-100 text-green-700"
              : profile.vetting_status === "PENDING"
              ? "bg-yellow-100 text-yellow-700"
              : "bg-red-100 text-red-600"
          }`}>
            {profile.vetting_status}
          </span>
        </div>

        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-2">Assigned Groups</p>
          {groups.length === 0 ? (
            <p className="text-xs text-gray-400">No groups assigned yet.</p>
          ) : (
            <ul className="space-y-1">
              {groups.map((g) => (
                <li key={g.id}>
                  <button
                    onClick={() => setActiveCommunity(g)}
                    className={`w-full text-left text-sm px-2 py-1.5 rounded-lg transition ${
                      activeCommunity?.id === g.id
                        ? "bg-brand-50 text-brand-700 font-semibold"
                        : "text-gray-600 hover:bg-gray-50"
                    }`}
                  >
                    {g.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      <main className="flex-1">
        {activeCommunity ? (
          <>
            <h1 className="text-xl font-bold text-gray-900 mb-1">{activeCommunity.name}</h1>
            <p className="text-xs text-gray-400 mb-5">{activeCommunity.member_count} members · Read-only portal view</p>

            {posts.length === 0 ? (
              <div className="text-gray-400 text-sm text-center py-12">No posts in this community yet.</div>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <div key={post.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 font-bold text-xs">
                        {post.display_name.charAt(0)}
                      </div>
                      <span className="text-sm font-semibold text-brand-700">{post.display_name}</span>
                      <span className="text-xs text-gray-400">
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 whitespace-pre-wrap">{post.content}</p>
                    <p className="text-xs text-gray-400 mt-2">{post.upvotes} upvotes · {post.reply_count} replies</p>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="text-gray-400 text-center py-16">Select a group to view its feed.</div>
        )}
      </main>
    </div>
  );
}
