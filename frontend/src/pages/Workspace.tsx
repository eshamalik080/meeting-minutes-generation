import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import UploadDropzone from "../components/UploadDropzone";
import { type StatusResponse, getStatus } from "../lib/api";

const STAGE_LABELS: Record<string, string> = {
  preprocessing: "Preprocessing audio",
  transcribing: "Transcribing speech",
  diarizing: "Identifying speakers",
  extracting: "Extracting minutes with AI",
};

/**
 * Phase 4 checkpoint: uploads a file and polls job status. The full
 * animated progress UI and results dashboard (tabs, downloads) are built
 * in Phase 5 — this proves the upload -> job -> status loop works
 * end-to-end against the real backend in the meantime.
 */
export default function Workspace() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [pollError, setPollError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;

    async function poll() {
      try {
        const result = await getStatus(jobId!);
        if (!cancelled) {
          setStatus(result);
          setPollError(null);
        }
      } catch {
        if (!cancelled) setPollError("Couldn't reach the backend to check job status.");
      }
    }

    poll();
    const interval = setInterval(poll, 2000);
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

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        {status?.status === "completed" ? (
          <>
            <p className="text-lg font-semibold text-emerald-600">Minutes are ready!</p>
            <p className="mt-1 text-sm text-slate-500">
              The full results dashboard lands in Phase 5. For now, fetch the result directly:
            </p>
            <code className="mt-4 block break-all rounded-lg bg-slate-50 px-4 py-3 text-left text-xs text-slate-600">
              GET /api/result/{jobId}
            </code>
          </>
        ) : status?.status === "failed" ? (
          <>
            <p className="text-lg font-semibold text-rose-600">Processing failed</p>
            <p className="mt-1 text-sm text-slate-500">{status.error}</p>
          </>
        ) : (
          <>
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-indigo-500" />
            <p className="mt-4 font-medium text-slate-900">
              {status?.stage ? STAGE_LABELS[status.stage] ?? status.stage : "Starting up..."}
            </p>
            <p className="mt-1 text-sm text-slate-500">{status?.filename}</p>
          </>
        )}

        {pollError && <p className="mt-4 text-sm text-rose-600">{pollError}</p>}

        <p className="mt-6 text-xs text-slate-400">Job ID: {jobId}</p>
      </div>

      <div className="mt-6 text-center">
        <Link to="/app" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
          &larr; Upload a different recording
        </Link>
      </div>
    </div>
  );
}
