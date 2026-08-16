import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg px-6 py-32 text-center">
      <p className="text-sm font-semibold text-indigo-600">404</p>
      <p className="mt-2 text-lg font-medium text-slate-900">Page not found</p>
      <Link to="/" className="mt-6 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-700">
        &larr; Back to home
      </Link>
    </div>
  );
}
