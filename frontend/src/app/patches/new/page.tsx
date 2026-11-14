"use client";
import { useSearchParams } from "next/navigation";
import { PatchProposalForm } from "@/components/patches/PatchProposalForm";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
export default function NewPatchPage() { const params = useSearchParams(); const id = Number(params.get("investigationId")); return <main className="space-y-6"><PageHeader eyebrow="Remediation" title="Create patch proposal" description="Submit a user-supplied remediation proposal for human review." /><Card className="p-6"><PatchProposalForm investigationId={Number.isInteger(id) && id > 0 ? id : undefined} /></Card></main>; }
