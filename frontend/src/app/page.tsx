"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getPOs } from "@/lib/api";
import { POListItem, POStatus } from "@/lib/types";
import { useUser } from "@/context/UserContext";

const statusStyles: Record<POStatus, string> = {
  Draft: "bg-zinc-100 text-zinc-600",
  "Pending Manager Approval": "bg-amber-100 text-amber-700",
  "Pending IT Validation": "bg-blue-100 text-blue-700",
  "Pending Finance Approval": "bg-orange-100 text-orange-700",
  Invoiced: "bg-green-100 text-green-700",
  "Needs Rework": "bg-red-100 text-red-700",
};

export default function HomePage() {
  const { currentUser } = useUser();
  const [pos, setPos] = useState<POListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPOs()
      .then(setPos)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900">Purchase Orders</h1>
          <p className="mt-1 text-sm text-zinc-500">{pos.length} total</p>
        </div>
        {currentUser?.role === "creator" && (
          <Link
            href="/po/new"
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 transition-colors"
          >
            + New PO
          </Link>
        )}
      </div>

      {loading ? (
        <p className="text-sm text-zinc-400">Loading...</p>
      ) : pos.length === 0 ? (
        <p className="text-sm text-zinc-400">No purchase orders found.</p>
      ) : (
        <div className="overflow-hidden rounded-xl border border-zinc-200">
          <table className="w-full text-sm">
            <thead className="bg-zinc-50 text-left text-xs font-medium uppercase tracking-wide text-zinc-500">
              <tr>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created by</th>
                <th className="px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 bg-white">
              {pos.map((po) => (
                <tr
                  key={po.id}
                  className="cursor-pointer hover:bg-zinc-50 transition-colors"
                  onClick={() => window.location.href = `/po/${po.id}`}
                >
                  <td className="px-4 py-3 font-medium text-zinc-900">{po.title}</td>
                  <td className="px-4 py-3 text-zinc-600">
                    ${po.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3 text-zinc-600">{po.category}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[po.status]}`}>
                      {po.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-zinc-600">{po.creator.username}</td>
                  <td className="px-4 py-3 text-zinc-400">
                    {new Date(po.created_at).toLocaleDateString("en-GB")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
