export type UserRole = "creator" | "manager" | "it_rep" | "finance";

export type POStatus =
  | "Draft"
  | "Pending Manager Approval"
  | "Pending IT Validation"
  | "Pending Finance Approval"
  | "Invoiced"
  | "Needs Rework";

export type POCategory = "Services" | "Office Supplies" | "IT Equipment";

export interface User {
  id: number;
  username: string;
  role: UserRole;
}

export interface AuditLog {
  id: number;
  action: string;
  note: string | null;
  timestamp: string;
  performed_by_user: User;
}

export interface POListItem {
  id: number;
  title: string;
  amount: number;
  category: POCategory;
  status: POStatus;
  created_at: string;
  creator: User;
}

export interface PO extends POListItem {
  description: string | null;
  rejection_reason: string | null;
  updated_at: string | null;
  audit_logs: AuditLog[];
}
