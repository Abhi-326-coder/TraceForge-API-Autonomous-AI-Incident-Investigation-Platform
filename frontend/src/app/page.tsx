import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-zinc-100">
      <div className="text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-emerald-400">
          TraceForge
        </p>

        <h1 className="mt-4 text-4xl font-bold">
          Autonomous Incident Investigation
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-zinc-400">
          Investigate production incidents using
          AI agents, observability data, source code,
          and organizational knowledge.
        </p>

        <Link
          href="/incidents/1"
          className="mt-8 inline-flex rounded-lg bg-zinc-100 px-5 py-3 text-sm font-medium text-zinc-950 transition hover:bg-white"
        >
          Open Demo Investigation
        </Link>
      </div>
    </main>
  );
}