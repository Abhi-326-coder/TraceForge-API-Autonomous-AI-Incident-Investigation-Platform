from app.agents.patch_agent import PatchAgent

agent = PatchAgent()

patch = agent.generate(
    incident={
        "title": "Checkout API returning HTTP 500 errors",
        "service": "checkout-api",
    },
    remediation={
        "title": "Improve database connection handling",
        "summary": (
            "Inspect connection acquisition and release. "
            "Do not increase pool size without supporting evidence."
        ),
        "evidence_ids": [1, 2],
    },
    source_files=[
        {
            "path": "app/checkout.py",
            "content": (
                "def checkout(db):\n"
                "    return db.execute('SELECT 1')\n"
            ),
        }
    ],
)

print(patch.model_dump_json(indent=2))