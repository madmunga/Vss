import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex flex-col items-center justify-center min-h-[40vh] text-center px-4">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-gray-800 mb-2">Something went wrong</h2>
            <p className="text-gray-500 text-sm mb-6 max-w-sm">{this.state.message || "An unexpected error occurred."}</p>
            <button
              onClick={() => { this.setState({ hasError: false, message: "" }); window.location.reload(); }}
              className="bg-brand-600 text-white px-5 py-2 rounded-xl text-sm hover:bg-brand-700 transition"
            >
              Reload page
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
