import { type ReactNode, createContext, useContext, useEffect, useState } from "react";

import * as authApi from "../lib/auth";

const TOKEN_STORAGE_KEY = "meeting_minutes_auth_token";

interface AuthContextValue {
  email: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }
    authApi
      .fetchCurrentUser(token)
      .then((user) => {
        if (user) setEmail(user.email);
        else localStorage.removeItem(TOKEN_STORAGE_KEY);
      })
      .finally(() => setIsLoading(false));
  }, []);

  async function login(emailInput: string, password: string) {
    const res = await authApi.login(emailInput, password);
    localStorage.setItem(TOKEN_STORAGE_KEY, res.access_token);
    setEmail(res.email);
  }

  async function signup(emailInput: string, password: string) {
    const res = await authApi.signup(emailInput, password);
    localStorage.setItem(TOKEN_STORAGE_KEY, res.access_token);
    setEmail(res.email);
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setEmail(null);
  }

  return <AuthContext.Provider value={{ email, isLoading, login, signup, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
