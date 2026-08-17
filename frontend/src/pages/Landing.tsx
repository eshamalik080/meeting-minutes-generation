import { AudioLines, Download, Sparkles, Users } from "lucide-react";
import { Link } from "react-router-dom";

import Reveal from "../components/Reveal";

const FEATURES = [
  {
    icon: AudioLines,
    title: "Accurate transcription",
    description: "Whisper-based speech-to-text turns your recording into a clean, timestamped transcript.",
  },
  {
    icon: Users,
    title: "Speaker diarization",
    description: "Automatically separates who said what, so the transcript reads like a real conversation.",
  },
  {
    icon: Sparkles,
    title: "AI-extracted minutes",
    description: "An LLM pulls out the summary, key topics, decisions, and action items with owners and deadlines.",
  },
  {
    icon: Download,
    title: "Export anywhere",
    description: "Download polished minutes as JSON, HTML, or PDF — ready to share right after the meeting ends.",
  },
];

const STEPS = [
  { number: "01", title: "Upload", description: "Drop in a Zoom, Meet, or phone recording — mp3, mp4, or wav." },
  { number: "02", title: "Transcribe & diarize", description: "Speech is transcribed and split by speaker automatically." },
  { number: "03", title: "AI extraction", description: "An LLM extracts the summary, decisions, and action items." },
  { number: "04", title: "Download", description: "Get structured minutes as JSON, HTML, or a shareable PDF." },
];

export default function Landing() {
  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-b from-indigo-950 via-indigo-900 to-slate-950">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(129,140,248,0.25),_transparent_60%)]" />
        <div
          aria-hidden
          className="animate-blob pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl"
        />
        <div
          aria-hidden
          className="animate-blob-delayed pointer-events-none absolute -right-16 top-32 h-80 w-80 rounded-full bg-violet-500/15 blur-3xl"
        />
        <div className="relative mx-auto max-w-4xl px-6 py-28 text-center">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1 text-xs font-medium text-indigo-200">
            <Sparkles className="h-3.5 w-3.5" />
            ASR + LLM powered
          </span>
          <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Meeting recordings in.
            <br />
            Structured minutes out.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-indigo-100/80">
            Upload any meeting recording and get a speaker-labeled transcript, an AI-generated summary,
            decisions, and action items — automatically, in minutes.
          </p>
          <div className="mt-9 flex items-center justify-center gap-4">
            <Link
              to="/app"
              className="rounded-lg bg-white px-6 py-3 text-sm font-semibold text-indigo-950 shadow-lg shadow-indigo-950/30 transition-all duration-200 ease-out hover:-translate-y-0.5 hover:bg-indigo-50 hover:shadow-xl hover:shadow-indigo-950/40 active:translate-y-0"
            >
              Get Started — it&apos;s free
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, description }, i) => (
            <Reveal key={title} delayMs={i * 75}>
              <div className="shine-card group h-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 ease-out hover:-translate-y-1 hover:border-indigo-200 hover:shadow-lg">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 transition-colors duration-300 group-hover:bg-indigo-100">
                  <Icon className="h-5 w-5" strokeWidth={2} />
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{description}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="bg-white py-20">
        <div className="mx-auto max-w-5xl px-6">
          <Reveal>
            <h2 className="text-center text-2xl font-semibold tracking-tight text-slate-900">How it works</h2>
          </Reveal>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((step, i) => (
              <Reveal key={step.number} delayMs={i * 75}>
                <div className="shine-card h-full rounded-2xl border border-transparent p-4 transition-all duration-300 ease-out hover:-translate-y-1 hover:border-indigo-100 hover:bg-indigo-50/40 hover:shadow-md">
                  <span className="text-sm font-semibold text-indigo-500">{step.number}</span>
                  <h3 className="mt-2 font-semibold text-slate-900">{step.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{step.description}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-slate-50 py-8">
        <p className="text-center text-sm text-slate-400">
          Automated Meeting Minutes Generation using ASR &amp; LLMs — capstone project
        </p>
      </footer>
    </div>
  );
}
