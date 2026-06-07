"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/lib/types";
import { getUsers } from "@/lib/api";

interface UserContextValue {
  users: User[];
  currentUser: User | null;
  setCurrentUser: (user: User) => void;
}

const UserContext = createContext<UserContextValue | null>(null);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    getUsers().then((data) => {
      setUsers(data);
      setCurrentUser(data[0] ?? null);
    });
  }, []);

  return (
    <UserContext.Provider value={{ users, currentUser, setCurrentUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used inside UserProvider");
  return ctx;
}