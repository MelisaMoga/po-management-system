"use client";

import Link from "next/link";
import { useUser } from "@/context/UserContext";

const roleLabels: Record<string, string> = {
  creator: "Creator",
  manager: "Manager",
  it_rep: "IT Rep",
  finance: "Finance",
};

export default function Header() {
  const { users, currentUser, setCurrentUser } = useUser();

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold tracking-tight text-zinc-900">
          PO Manager
        </Link>

        <div className="flex items-center gap-3">
          <span className="text-sm text-zinc-500">Acting as</span>
          <select
            className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-1.5 text-sm font-medium text-zinc-800 focus:outline-none focus:ring-2 focus:ring-zinc-400"
            value={currentUser?.id ?? ""}
            onChange={(e) => {
              const selected = users.find((u) => u.id === Number(e.target.value));
              if (selected) setCurrentUser(selected);
            }}
          >
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.username} - {roleLabels[u.role] ?? u.role}
              </option>
            ))}
          </select>

          {currentUser && (
            <span className="rounded-full bg-zinc-900 px-2.5 py-0.5 text-xs font-medium text-white">
              {roleLabels[currentUser.role] ?? currentUser.role}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}