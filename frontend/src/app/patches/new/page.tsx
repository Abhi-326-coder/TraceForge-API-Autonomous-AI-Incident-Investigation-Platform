"use client";
import { useSearchParams } from "next/navigation";
import { PatchProposalForm } from "@/components/patches/PatchProposalForm";
import { GenerateAIPatch } from "@/components/patches/GenerateAIPatch";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
export default function NewPatchPage() { const params = useSearchParams(); const id = Number(params.get("investigationId")); const investigationId = Number.isInteger(id) && id > 0 ? id : undefined; return <main className="space-y-6"><PageHeader eyebrow="Remediation" title="Create patch proposal" description="Generate an evidence-based AI proposal or submit your own patch for human review." /><GenerateAIPatch investigationId={investigationId} /><Card className="p-6"><PatchProposalForm investigationId={investigationId} /></Card></main>; }
