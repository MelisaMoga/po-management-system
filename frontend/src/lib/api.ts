import { User, POListItem, PO } from "./types";

const BASE_URL = "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }
  return res.json();
}

export function getUsers(): Promise<User[]> {
  return request<User[]>("/api/users/");
}

export function getPOs(): Promise<POListItem[]> {
  return request<POListItem[]>("/api/po/");
}

export function getPO(id: number): Promise<PO> {
  return request<PO>(`/api/po/${id}`);
}

export function createPO(data: {
  title: string;
  description?: string;
  amount: number;
  category: string;
  created_by: number;
}): Promise<PO> {
  return request<PO>("/api/po/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function updatePO(
  id: number,
  userId: number,
  data: { title?: string; description?: string; amount?: number; category?: string }
): Promise<PO> {
  return request<PO>(`/api/po/${id}?user_id=${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function submitPO(id: number, userId: number): Promise<PO> {
  return request<PO>(`/api/po/${id}/submit?user_id=${userId}`, { method: "POST" });
}

export function approvePO(id: number, userId: number): Promise<PO> {
  return request<PO>(`/api/po/${id}/approve?user_id=${userId}`, { method: "POST" });
}

export function rejectPO(id: number, userId: number, reason: string): Promise<PO> {
  return request<PO>(
    `/api/po/${id}/reject?user_id=${userId}&reason=${encodeURIComponent(reason)}`,
    { method: "POST" }
  );
}

export function resubmitPO(id: number, userId: number): Promise<PO> {
  return request<PO>(`/api/po/${id}/resubmit?user_id=${userId}`, { method: "POST" });
}