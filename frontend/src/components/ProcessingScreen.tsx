import { AudioLines, Check, Sparkles, Users, Waypoints } from "lucide-react";

import type { StatusResponse } from "../lib/api";

const STAGES = [
  { key: "preprocessing", label: "Preprocessing audio", description: "Normalizing and cleaning the recording", icon: AudioLines },
  { key: "transcribing", label: "Transcribing speech", description: "Converting speech to text with Whisper", icon: Waypoints },
  { key: "diarizing", label: "Identifying speakers", description: "Working out who said what", icon: Users },
  { key: "extracting", label: "Extracting minutes", description: "Summarizing, decisions, and action items with AI", icon: Sparkles },
] as const;

interface ProcessingScreenProps {
  status: StatusResponse;
}

export default function ProcessingScreen({ status }: ProcessingScreenProps) {
  const currentIndex = status.stage ? STAGES.findIndex((s) => s.key === status.stage) : -1;

  return (
    <div className="animate-fade-in mx-auto max-w-lg px-6 py-20">
      <div className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Generating your minutes</h1>
        <p className="mt-2 truncate text-sm text-slate-500">{status.filename}</p>
      </div>

      <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <ol className="space-y-0">
          {STAGES.map((stage, index) => {
            const isDone = currentIndex > index;
            const isActive = index === currentIndex;
            const isPending = currentIndex === -1 || index > currentIndex;
            const Icon = stage.icon;

            return (
              <li key={stage.key} className="relative flex gap-4 pb-8 last:pb-0">
                {index < STAGES.length - 1 && (
                  <span
                    className={`absolute left-[19px] top-10 h-[calc(100%-2.5rem)] w-px transition-colors duration-300 ${
                      isDone ? "bg-indigo-300" : "bg-slate-200"
                    }`}
                  />
                )}
                <span
                  className={`relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 transition-colors duration-300 ${
                    isDone
                      ? "border-indigo-600 bg-indigo-600 text-white"
                      : isActive
                        ? "border-indigo-500 bg-indigo-50 text-indigo-600"
                        : "border-slate-200 bg-white text-slate-300"
                  }`}
                >
                  {isDone ? (
                    <Check className="h-5 w-5" strokeWidth={2.5} />
                  ) : (
                    <Icon className={`h-5 w-5 ${isActive ? "animate-pulse" : ""}`} strokeWidth={2} />
                  )}
                </span>
                <div className="pt-1.5">
                  <p className={`font-medium transition-colors duration-300 ${isPending ? "text-slate-400" : "text-slate-900"}`}>
                    {stage.label}
                  </p>
                  <p className={`text-sm transition-colors duration-300 ${isPending ? "text-slate-300" : "text-slate-500"}`}>
                    {stage.description}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>

      <p className="mt-6 text-center text-xs text-slate-400">Job ID: {status.job_id}</p>
    </div>
  );
}
