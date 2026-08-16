import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled error in UI:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="mx-auto max-w-lg px-6 py-32 text-center">
          <p className="text-lg font-medium text-slate-900">Something went wrong</p>
          <p className="mt-1 text-sm text-slate-500">
            The app hit an unexpected error. Try reloading the page.
          </p>
          <a href="/" className="mt-6 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-700">
            &larr; Back to home
          </a>
        </div>
      );
    }
    return this.props.children;
  }
}
