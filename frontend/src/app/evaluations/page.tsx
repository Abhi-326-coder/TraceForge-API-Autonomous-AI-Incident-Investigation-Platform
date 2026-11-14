"use client";

import { useEvaluationDashboard } from "@/hooks/use-evaluation-dashboard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { PageHeader } from "@/components/ui/PageHeader";

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
    <Card className="p-5">
      <p className="text-sm text-muted-foreground">{title}</p>
      <h2 className="mt-2 text-3xl font-semibold">{value}</h2>
      <p className="mt-2 text-xs text-muted-foreground">
        {description}
      </p>
    </Card>
  );
}

export default function EvaluationPage() {
  const { data, isLoading, isError, error, refetch } = useEvaluationDashboard();

  if (isLoading) {
    return (
      <div className="space-y-4"><LoadingSkeleton className="h-8 w-56" /><LoadingSkeleton className="h-32 w-full" /></div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Unable to load evaluations"
        description={error instanceof Error ? error.message : "Unable to load dashboard."}
        onRetry={() => refetch()}
      />
    );
  }

  const percent = (value: number) =>
    `${(value * 100).toFixed(1)}%`;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Analytics"
        title="Evaluation dashboard"
        description="Monitor investigation quality and system performance."
        actions={<Button variant="secondary" onClick={() => refetch()}>Refresh results</Button>}
      />

      <Card className="p-4">
        <p className="text-sm font-medium">Evaluation mode</p>
        <p className="mt-1 text-sm text-muted-foreground">
          {data.mode}
        </p>
        <p className="mt-2 text-xs text-muted-foreground">
          These are deterministic fixture smoke-test results,
          not measured live AI accuracy.
        </p>
      </Card>

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

        <div className="overflow-x-auto rounded-xl border bg-surface">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface-subtle">
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
    </div>
  );
}
