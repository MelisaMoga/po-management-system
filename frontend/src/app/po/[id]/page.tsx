"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useUser } from "@/context/UserContext";
import { getPO, submitPO, approvePO, rejectPO, resubmitPO } from "@/lib/api";
import { PO, POStatus } from "@/lib/types";

const statusStyles: Record<POStatus, string> = {
  Draft: "bg-zinc-100 text-zinc-600",
  "Pending Manager Approval": "bg-amber-100 text-amber-700",
  "Pending IT Validation": "bg-blue-100 text-blue-700",
  "Pending Finance Approval": "bg-orange-100 text-orange-700",
  Invoiced: "bg-green-100 text-green-700",
  "Needs Rework": "bg-red-100 text-red-700",
};

export default function PODetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { currentUser } = useUser();

  const [po, setPo] = useState<PO | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getPO(Number(id))
      .then(setPo)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleAction(action: () => Promise<PO>) {
    setBusy(true);
    setActionError(null);
    try {
      const updated = await action();
      setPo(updated);
      setShowRejectForm(false);
      setRejectReason("");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <div className="mx-auto max-w-3xl px-6 py-10 text-sm text-zinc-400">Loading...</div>;
  if (!po) return <div className="mx-auto max-w-3xl px-6 py-10 text-sm text-red-500">PO not found.</div>;
  if (!currentUser) return null;

  const isCreator = currentUser.role === "creator" && po.creator.id === currentUser.id;
  const canSubmit = isCreator && po.status === "Draft";
  const canResubmit = isCreator && po.status === "Needs Rework";
  const canApprove =
    (currentUser.role === "manager" && po.status === "Pending Manager Approval") ||
    (currentUser.role === "it_rep" && po.status === "Pending IT Validation") ||
    (currentUser.role === "finance" && po.status === "Pending Finance Approval");

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">

      {/* Back link */}
      <button onClick={() => router.push("/")} className="mb-6 text-sm text-zinc-400 hover:text-zinc-700 transition-colors">
        ← Back to list
      </button>

      {/* PO Header */}
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900">{po.title}</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Created by <span className="font-medium">{po.creator.username}</span> on{" "}
            {new Date(po.created_at).toLocaleDateString("en-GB")}
          </p>
        </div>
        <span className={`shrink-0 rounded-full px-3 py-1 text-sm font-medium ${statusStyles[po.status]}`}>
          {po.status}
        </span>
      </div>

      {/* Details */}
      <div className="mb-8 rounded-xl border border-zinc-200 bg-white p-6">
        <dl className="grid grid-cols-2 gap-x-8 gap-y-4 text-sm">
          <div>
            <dt className="text-zinc-500">Amount</dt>
            <dd className="mt-0.5 font-medium text-zinc-900">
              ${po.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </dd>
          </div>
          <div>
            <dt className="text-zinc-500">Category</dt>
            <dd className="mt-0.5 font-medium text-zinc-900">{po.category}</dd>
          </div>
          {po.description && (
            <div className="col-span-2">
              <dt className="text-zinc-500">Description</dt>
              <dd className="mt-0.5 text-zinc-900">{po.description}</dd>
            </div>
          )}
          {po.rejection_reason && (
            <div className="col-span-2">
              <dt className="text-zinc-500">Rejection reason</dt>
              <dd className="mt-0.5 text-red-600">{po.rejection_reason}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* Actions */}
      {(canSubmit || canResubmit || canApprove) && (
        <div className="mb-8 flex flex-col gap-3">
          {actionError && <p className="text-sm text-red-500">{actionError}</p>}

          <div className="flex gap-3">
            {canSubmit && (
              <button
                disabled={busy}
                onClick={() => handleAction(() => submitPO(po.id, currentUser.id))}
                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 transition-colors disabled:opacity-50"
              >
                Submit for Approval
              </button>
            )}

            {canResubmit && (
              <button
                disabled={busy}
                onClick={() => handleAction(() => resubmitPO(po.id, currentUser.id))}
                className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 transition-colors disabled:opacity-50"
              >
                Resubmit
              </button>
            )}

            {canApprove && (
              <>
                <button
                  disabled={busy}
                  onClick={() => handleAction(() => approvePO(po.id, currentUser.id))}
                  className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  disabled={busy}
                  onClick={() => { setShowRejectForm(true); setActionError(null); }}
                  className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                >
                  Reject
                </button>
              </>
            )}
          </div>

          {showRejectForm && (
            <div className="flex flex-col gap-2 rounded-lg border border-zinc-200 bg-zinc-50 p-4">
              <label className="text-sm font-medium text-zinc-700">Reason for rejection</label>
              <textarea
                rows={3}
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Explain why this PO is being rejected..."
                className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400"
              />
              <div className="flex gap-2">
                <button
                  disabled={busy || !rejectReason.trim()}
                  onClick={() => handleAction(() => rejectPO(po.id, currentUser.id, rejectReason))}
                  className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  Confirm Rejection
                </button>
                <button
                  onClick={() => { setShowRejectForm(false); setRejectReason(""); }}
                  className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-100 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Audit Log */}
      <div>
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-zinc-500">Audit Log</h2>
        {po.audit_logs.length === 0 ? (
          <p className="text-sm text-zinc-400">No activity yet.</p>
        ) : (
          <ol className="flex flex-col gap-3">
            {po.audit_logs.map((log) => (
              <li key={log.id} className="flex gap-4 text-sm">
                <span className="w-32 shrink-0 text-zinc-400">
                  {new Date(log.timestamp).toLocaleDateString("en-GB")}
                </span>
                <div>
                  <span className="font-medium text-zinc-900">{log.action}</span>
                  {log.note && <span className="text-zinc-500"> - {log.note}</span>}
                  <span className="text-zinc-400"> by {log.performed_by_user.username}</span>
                </div>
              </li>
            ))}
          </ol>
        )}
      </div>

    </div>
  );
}
