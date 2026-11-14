export function DiffReview({ diff }: { diff: string }) { return <pre className="max-h-[32rem] overflow-auto rounded-lg bg-slate-950 p-4 text-xs leading-5 text-slate-100"><code>{diff}</code></pre>; }
