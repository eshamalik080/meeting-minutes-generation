import { CheckCircle2, Clock, Download, FileJson, FileText, ListChecks, MessageSquare, Sparkles, Users } from "lucide-react";
import { useState } from "react";

import { type ExportFormat, type MeetingMinutes, exportUrl } from "../lib/api";
import { formatDateTime, formatDuration, formatTimestamp } from "../lib/format";

const TABS = [
  { key: "summary", label: "Summary", icon: Sparkles },
  { key: "transcript", label: "Transcript", icon: MessageSquare },
  { key: "decisions", label: "Decisions", icon: CheckCircle2 },
  { key: "actions", label: "Action Items", icon: ListChecks },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const EXPORTS: { format: ExportFormat; label: string; icon: typeof FileJson }[] = [
  { format: "json", label: "JSON", icon: FileJson },
  { format: "html", label: "HTML", icon: FileText },
  { format: "pdf", label: "PDF", icon: FileText },
];

interface ResultsDashboardProps {
  minutes: MeetingMinutes;
}

export default function ResultsDashboard({ minutes }: ResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("summary");

  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Meeting Minutes</h1>
          <p className="mt-1 truncate text-sm text-slate-500">
            {minutes.source_filename} &middot; Generated {formatDateTime(minutes.generated_at)}
            {minutes.duration_seconds != null && <> &middot; {formatDuration(minutes.duration_seconds)}</>}
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          {EXPORTS.map(({ format, label, icon: Icon }) => (
            <a
              key={format}
              href={exportUrl(minutes.job_id, format)}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-indigo-300 hover:text-indigo-600"
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
              {label}
              <Download className="h-3.5 w-3.5 text-slate-400" strokeWidth={2} />
            </a>
          ))}
        </div>
      </div>

      {minutes.participants.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <Users className="h-4 w-4 text-slate-400" strokeWidth={2} />
          {minutes.participants.map((p) => (
            <span key={p} className="rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-medium text-slate-600">
              {p}
            </span>
          ))}
        </div>
      )}

      <div className="mt-8 flex gap-1 border-b border-slate-200">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            type="button"
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-1.5 border-b-2 px-4 py-2.5 text-sm font-medium transition ${
              activeTab === key
                ? "border-indigo-600 text-indigo-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <Icon className="h-4 w-4" strokeWidth={2} />
            {label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {activeTab === "summary" && <SummaryTab minutes={minutes} />}
        {activeTab === "transcript" && <TranscriptTab minutes={minutes} />}
        {activeTab === "decisions" && <DecisionsTab minutes={minutes} />}
        {activeTab === "actions" && <ActionItemsTab minutes={minutes} />}
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center text-sm text-slate-400">{message}</p>;
}

function SummaryTab({ minutes }: { minutes: MeetingMinutes }) {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-indigo-600">Summary</h2>
        <p className="mt-3 leading-relaxed text-slate-700">{minutes.summary || "No summary available."}</p>
      </div>

      {minutes.key_topics.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xs font-semibold uppercase tracking-wide text-indigo-600">Key Topics</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {minutes.key_topics.map((topic) => (
              <span key={topic} className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-600">
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TranscriptTab({ minutes }: { minutes: MeetingMinutes }) {
  if (minutes.transcript.length === 0) return <EmptyState message="No transcript available." />;
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="divide-y divide-slate-100">
        {minutes.transcript.map((seg, i) => (
          <div key={i} className="flex gap-4 py-3 first:pt-0 last:pb-0">
            <span className="flex items-center gap-1.5 pt-0.5 text-xs text-slate-400">
              <Clock className="h-3.5 w-3.5" strokeWidth={2} />
              <span className="font-mono tabular-nums">{formatTimestamp(seg.start)}</span>
            </span>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-indigo-600">{seg.speaker}</p>
              <p className="mt-0.5 leading-relaxed text-slate-700">{seg.text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DecisionsTab({ minutes }: { minutes: MeetingMinutes }) {
  if (minutes.decisions.length === 0) return <EmptyState message="No decisions were recorded." />;
  return (
    <ul className="space-y-3">
      {minutes.decisions.map((decision, i) => (
        <li key={i} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" strokeWidth={2} />
          <p className="text-slate-700">{decision}</p>
        </li>
      ))}
    </ul>
  );
}

function ActionItemsTab({ minutes }: { minutes: MeetingMinutes }) {
  if (minutes.action_items.length === 0) return <EmptyState message="No action items were recorded." />;
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <th className="px-5 py-3 font-medium">Task</th>
            <th className="px-5 py-3 font-medium">Owner</th>
            <th className="px-5 py-3 font-medium">Deadline</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {minutes.action_items.map((item, i) => (
            <tr key={i}>
              <td className="px-5 py-3.5 text-slate-700">{item.task}</td>
              <td className="px-5 py-3.5">
                <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-600">{item.owner}</span>
              </td>
              <td className="px-5 py-3.5 text-slate-500">{item.deadline}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
