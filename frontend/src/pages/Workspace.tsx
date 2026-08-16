import { AlertTriangle, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import ProcessingScreen from "../components/ProcessingScreen";
import ResultsDashboard from "../components/ResultsDashboard";
import UploadDropzone from "../components/UploadDropzone";
import { ApiError, type MeetingMinutes, type StatusResponse, getResult, getStatus } from "../lib/api";

function describeError(err: unknown, fallback: string): string {
  if (err instanceof ApiError) {
    return err.status === 404 ? "This job doesn't exist — it may have expired or the link is wrong." : err.message;
  }
  return fallback;
}

const POLL_INTERVAL_MS = 2000;

export default function Workspace() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [minutes, setMinutes] = useState<MeetingMinutes | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    setStatus(null);
    setMinutes(null);
    setError(null);

    let cancelled = false;
    let interval: ReturnType<typeof setInterval>;

    async function poll() {
      try {
        const result = await getStatus(jobId!);
        if (cancelled) return;
        setStatus(result);

        if (result.status === "completed") {
          clearInterval(interval);
          try {
            const fullResult = await getResult(jobId!);
            if (!cancelled) setMinutes(fullResult);
          } catch (err) {
            if (!cancelled) setError(describeError(err, "Job completed, but the results couldn't be loaded."));
          }
        } else if (result.status === "failed") {
          clearInterval(interval);
        }
      } catch (err) {
        clearInterval(interval);
        if (!cancelled) setError(describeError(err, "Couldn't reach the backend to check job status."));
      }
    }

    poll();
    interval = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [jobId]);

  if (!jobId) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-20">
        <div className="text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Upload a meeting recording</h1>
          <p className="mt-2 text-slate-500">We'll transcribe it, identify speakers, and extract structured minutes.</p>
        </div>
        <div className="mt-10">
          <UploadDropzone onUploaded={(id) => navigate(`/app/${id}`)} />
        </div>
      </div>
    );
  }

  if (error && !status) {
    return <ErrorScreen message={error} />;
  }

  if (status?.status === "failed") {
    return <ErrorScreen message={status.error ?? "Something went wrong while processing this recording."} />;
  }

  if (status?.status === "completed" && minutes) {
    return <ResultsDashboard minutes={minutes} />;
  }

  if (status?.status === "completed" && !minutes) {
    return (
      <div className="mx-auto max-w-lg px-6 py-32 text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-500" />
        <p className="mt-4 text-slate-500">{error ?? "Loading results..."}</p>
      </div>
    );
  }

  if (status) {
    return <ProcessingScreen status={status} />;
  }

  return (
    <div className="mx-auto max-w-lg px-6 py-32 text-center">
      <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-500" />
      <p className="mt-4 text-slate-500">Loading job...</p>
    </div>
  );
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="mx-auto max-w-lg px-6 py-32 text-center">
      <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-500">
        <AlertTriangle className="h-6 w-6" strokeWidth={2} />
      </span>
      <p className="mt-4 font-medium text-slate-900">Something went wrong</p>
      <p className="mt-1 text-sm text-slate-500">{message}</p>
      <Link to="/app" className="mt-6 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-700">
        &larr; Try a different recording
      </Link>
    </div>
  );
}
