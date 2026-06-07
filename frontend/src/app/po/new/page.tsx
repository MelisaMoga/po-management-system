"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/context/UserContext";
import { createPO } from "@/lib/api";
import { POCategory } from "@/lib/types";

const categories: POCategory[] = ["Services", "Office Supplies", "IT Equipment"];

export default function NewPOPage() {
  const { currentUser } = useUser();
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState<POCategory>("Services");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (currentUser && currentUser.role !== "creator") {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <p className="text-sm text-red-500">Only creators can create purchase orders.</p>
      </div>
    );
  }

  async function handleSubmit() {
    if (!currentUser) return;
    setSubmitting(true);
    setError(null);
    try {
      const po = await createPO({
        title,
        description: description || undefined,
        amount: parseFloat(amount),
        category,
        created_by: currentUser.id,
      });
      router.push(`/po/${po.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setSubmitting(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400";

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-8 text-2xl font-semibold text-zinc-900">New Purchase Order</h1>

      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="flex flex-col gap-5">
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-zinc-700">Title</label>
          <input
            type="text"
            required
            placeholder="e.g. Laptops for dev team"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={inputClass}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium text-zinc-700">
            Description <span className="font-normal text-zinc-400">(optional)</span>
          </label>
          <textarea
            rows={3}
            placeholder="Additional details..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={inputClass}
          />
        </div>

        <div className="flex gap-4">
          <div className="flex flex-1 flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700">Amount ($)</label>
            <input
              type="number"
              required
              min="0.01"
              step="0.01"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className={inputClass}
            />
          </div>

          <div className="flex flex-1 flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as POCategory)}
              className={inputClass}
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => router.push("/")}
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 transition-colors disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Create PO"}
          </button>
        </div>
      </form>
    </div>
  );
}