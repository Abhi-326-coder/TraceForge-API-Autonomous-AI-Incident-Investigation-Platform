"use client";

import { useQuery } from "@tanstack/react-query";
import { getEvaluationDashboard } from "@/lib/evaluation";

function MetricCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <p className="text-sm text-muted-foreground">{title}</p>
      <h2 className="mt-2 text-3xl font-semibold">{value}</h2>
      <p className="mt-2 text-xs text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

export default function EvaluationPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["evaluation-dashboard"],
    queryFn: getEvaluationDashboard,
    retry: 1,
  });

  if (isLoading) {
    return (
      <main className="p-8">
        <p className="text-muted-foreground">
          Loading evaluation results...
        </p>
      </main>
    );
  }

  if (isError || !data) {
    return (
      <main className="space-y-4 p-8">
        <h1 className="text-2xl font-semibold">
          Evaluation Dashboard
        </h1>
        <p className="text-sm text-red-500">
          {error instanceof Error
            ? error.message
            : "Unable to load dashboard."}
        </p>
        <button
          onClick={() => refetch()}
          className="rounded-lg border px-4 py-2 text-sm"
        >
          Retry
        </button>
      </main>
    );
  }

  const percent = (value: number) =>
    `${(value * 100).toFixed(1)}%`;

  return (
    <main className="space-y-8 p-6 md:p-8">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">
            TRACEFORGE / ANALYTICS
          </p>
          <h1 className="mt-2 text-3xl font-semibold">
            Evaluation Dashboard
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Monitor investigation quality and system performance.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="rounded-lg border px-4 py-2 text-sm"
        >
          Refresh results
        </button>
      </header>

      <div className="rounded-xl border p-4">
        <p className="text-sm font-medium">Evaluation mode</p>
        <p className="mt-1 text-sm text-muted-foreground">
          {data.mode}
        </p>
        <p className="mt-2 text-xs text-muted-foreground">
          These are deterministic fixture smoke-test results,
          not measured live AI accuracy.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Pass rate"
          value={percent(data.pass_rate)}
          description={`${data.passed_cases} of ${data.total_cases} cases passed`}
        />

        <MetricCard
          title="Root-cause match"
          value={percent(data.root_cause_accuracy)}
          description="Fixture prediction matching"
        />

        <MetricCard
          title="Evidence grounding"
          value={percent(data.evidence_grounding_rate)}
          description="Evidence ID validation"
        />

        <MetricCard
          title="Average duration"
          value={`${data.average_duration_ms.toFixed(1)} ms`}
          description={`${data.average_tool_calls.toFixed(1)} average tool calls`}
        />
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">
            Evaluation cases
          </h2>
          <p className="text-sm text-muted-foreground">
            Individual fixture evaluation results.
          </p>
        </div>

        <div className="overflow-x-auto rounded-xl border">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="p-4">Test case</th>
                <th className="p-4">Root cause</th>
                <th className="p-4">Evidence</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>

            <tbody>
              {data.cases.map((item) => (
                <tr key={item.case_id} className="border-t">
                  <td className="p-4 font-medium">
                    {item.case_id}
                  </td>

                  <td className="p-4">
                    {item.root_cause_match ? "Matched" : "Failed"}
                  </td>

                  <td className="p-4">
                    {item.evidence_grounded &&
                    item.required_evidence_covered
                      ? "Grounded"
                      : "Needs review"}
                  </td>

                  <td className="p-4">
                    <span
                      className={
                        item.passed
                          ? "rounded-full bg-green-500/10 px-3 py-1 text-green-600"
                          : "rounded-full bg-red-500/10 px-3 py-1 text-red-600"
                      }
                    >
                      {item.passed ? "Passed" : "Failed"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}