import React, { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { auth } from "../../firebase";
import { signOut } from "firebase/auth";
import { config } from "../core/config";
import { Avatar, AvatarImage } from "@/components/ui/avatar";

interface LinkData {
  link_id: number;
  new_link: string;
  click_count: number;
  creator_id: string;
  old_link: string;
  expires_at: string;
  timeRegistered: string;
}


function UserProfile() {
  const [user, isLoading] = useAuth();
  const [userData, setUserData] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [draftName, setDraftName] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!user) return;
    let mounted = true;
    const fetchProfile = async () => {
      try {
        const token = await user.getIdToken();
        const user_id = user.uid;
        const res = await fetch(new URL(`user/${user_id}`, config.BASE_API_URL).href, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          console.error("Failed to fetch profile", res.status);
          return;
        }
        const json = await res.json();
        if (mounted) {
          setUserData(json);
          setDraftName(json.displayable_name || "");
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchProfile();
    return () => {
      mounted = false;
    };
  }, [user]);

  const saveName = async () => {
    if (!user) return;
    setIsSaving(true);
    const previous = userData?.displayable_name;
    // optimistic update
    setUserData((d: any) => ({ ...(d || {}), displayable_name: draftName }));

    try {
      const token = await user.getIdToken();
      const user_id = user.uid;
      // Fake endpoint: adjust path as you need. We PATCH the user resource.
      const res = await fetch(new URL(`user/${user_id}`, config.BASE_API_URL).href, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ displayable_name: draftName }),
      });
      if (!res.ok) {
        throw new Error(`Failed to save (${res.status})`);
      }
      // server response ignored — you said you'll take over server side
      setIsEditing(false);
      alert("Display name saved");
    } catch (err) {
      console.error(err);
      // rollback optimistic update
      setUserData((d: any) => ({ ...(d || {}), displayable_name: previous }));
      alert("Failed to save name — please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading || !userData) {
    return (
      <div className="p-6 bg-white rounded-lg shadow flex items-center gap-4 w-full max-w-sm">
        <div className="animate-pulse">
          <div className="w-20 h-20 bg-gray-200 rounded-full mb-2" />
        </div>
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-40 mb-2 animate-pulse" />
          <div className="h-3 bg-gray-200 rounded w-28 animate-pulse" />
        </div>
      </div>
    );
  }

  const { presigned_url_profile_pic, country, displayable_name, email } = userData;

  return (
    <div className="p-6 bg-white rounded-lg shadow w-full max-w-sm">
      <div className="flex items-center gap-4">
        <Avatar className="w-20 h-20">
          <AvatarImage src={presigned_url_profile_pic} alt={displayable_name || "avatar"} />
        </Avatar>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            {isEditing ? (
              <>
                <input
                  className="border rounded px-2 py-1 text-lg w-56"
                  value={draftName}
                  onChange={(e) => setDraftName(e.target.value)}
                  disabled={isSaving}
                />
                <button
                  className="px-3 py-1 rounded bg-green-600 text-white text-sm hover:bg-green-700"
                  onClick={saveName}
                  disabled={isSaving}
                >
                  {isSaving ? "Saving..." : "Save"}
                </button>
                <button
                  className="px-3 py-1 rounded border text-sm hover:bg-gray-50"
                  onClick={() => {
                    setIsEditing(false);
                    setDraftName(displayable_name || "");
                  }}
                  disabled={isSaving}
                >
                  Cancel
                </button>
              </>
            ) : (
              <>
                <h3 className="text-xl font-semibold text-gray-900 cursor-pointer hover:underline" onClick={() => setIsEditing(true)}>
                  {displayable_name || "No display name"}
                </h3>
                <button
                  className="ml-2 text-sm px-2 py-1 border rounded text-gray-600 hover:bg-gray-50"
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </button>
              </>
            )}
          </div>
          <div className="mt-2 text-sm text-gray-600">
            <div>{email}</div>
            <div className="mt-1">{country}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LinksTable() {
  const [user, isLoading] = useAuth();
  const [usageData, setUsageData] = useState<LinkData[] | null>(null);

  useEffect(() => {
    if (!user) return;
    let mounted = true;
    const handle_fetch = async () => {
      try {
        const token = await user.getIdToken();
        const user_id = user.uid;
        const request = await fetch(new URL(`user/${user_id}/links`, config.BASE_API_URL).href, {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!request.ok) {
          console.error(request.status);
          return;
        }
        const response = await request.json();
        if (mounted) setUsageData(response);
      } catch (e) {
        console.error(e);
      }
    };
    handle_fetch();
    return () => {
      mounted = false;
    };
  }, [user]);

  if (isLoading || usageData === null) {
    return (
      <div className="w-full max-w-4xl">
        <div className="h-48 bg-white rounded-lg shadow p-6 animate-pulse" />
      </div>
    );
  }

  if (usageData.length === 0) {
    return (
      <div className="w-full max-w-4xl">
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-600">No shortened links found. Create your first link!</div>
      </div>
    );
  }

  const formatStatus = (expires_at: string) => {
    const expiresAt = new Date(expires_at);
    const now = new Date();
    const isExpired = expiresAt < now;
    const isExpiringSoon = !isExpired && expiresAt.getTime() - now.getTime() < 24 * 60 * 60 * 1000;
    if (isExpired) return { text: "Expired", className: "text-red-700 bg-red-50" };
    if (isExpiringSoon) return { text: "Expiring Soon", className: "text-orange-700 bg-orange-50" };
    return { text: "Active", className: "text-green-700 bg-green-50" };
  };

  return (
    <div className="w-full max-w-4xl">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">Your Shortened Links</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Short</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Original</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clicks</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expires</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usageData.map((link) => {
                const status = formatStatus(link.expires_at);
                return (
                  <tr key={link.link_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-gray-900">{link.new_link}</span>
                        <button
                          className="text-xs px-2 py-1 rounded border hover:bg-gray-50"
                          onClick={() => navigator.clipboard.writeText(`${window.location.origin}/${link.new_link}`)}
                        >
                          Copy
                        </button>
                        <a
                          className="text-xs px-2 py-1 rounded border hover:bg-gray-50"
                          href={`${window.location.origin}/${link.new_link}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open
                        </a>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="max-w-xl truncate">
                        <a href={link.old_link} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:text-blue-800 truncate block" title={link.old_link}>
                          {link.old_link}
                        </a>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{link.click_count}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(link.timeRegistered).toLocaleDateString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.className}`}>{status.text}</span>
                      <div className="text-xs text-gray-500 mt-1">{new Date(link.expires_at).toLocaleDateString()}</div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default function User() {
  const [user, isLoading] = useAuth();

  const handleSignOut = async () => {
    await signOut(auth);
  };

  if (isLoading) {
    return <p className="p-6">Loading...</p>;
  }

  return (
    <div className="flex flex-col w-full h-full gap-6 p-6">
      <div className="flex flex-col md:flex-row gap-6">
        <UserProfile />
        <LinksTable />
      </div>

      <div className="flex w-full">
        <button className="mx-auto px-6 py-2 rounded bg-red-600 text-white hover:bg-red-700" onClick={handleSignOut}>
          Sign out
        </button>
      </div>
    </div>
  );
}
