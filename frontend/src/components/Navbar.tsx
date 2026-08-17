import { LogOut, Mic2, User } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { email, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Mic2 className="h-5 w-5" strokeWidth={2.25} />
          </span>
          Meeting Minutes AI
        </Link>
        <div className="flex items-center gap-3">
          {email ? (
            <>
              <span className="hidden items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 sm:flex">
                <User className="h-3.5 w-3.5" strokeWidth={2} />
                {email}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-900 hover:shadow-sm active:translate-y-0"
              >
                <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
                Log out
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="text-sm font-medium text-slate-600 transition-colors duration-200 hover:text-slate-900"
            >
              Log in
            </Link>
          )}
          <Link
            to="/app"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-all duration-200 ease-out hover:-translate-y-0.5 hover:bg-indigo-700 hover:shadow-md active:translate-y-0"
          >
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}
