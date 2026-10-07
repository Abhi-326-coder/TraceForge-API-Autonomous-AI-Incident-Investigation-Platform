## Add the Root cause Agent

- Add the schema for root cause result

```python
from pydantic import BaseModel, Field


class AlternativeCause(BaseModel):
    cause: str
    reason_not_primary: str


class RootCauseResult(BaseModel):
    root_cause: str

    explanation: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence_ids: list[int]

    alternative_causes: list[AlternativeCause]

    uncertainty: str
```

- Add the root cause agent in agents folder having the main function of analyze taking evidence intput and prompt - ``root_cause_agent.py``

- Add the ``root_cause_service.py`` to make sure the business logic lies in Service folder 

- Add the route ``POST api/incidents/{incident_id}/root-cause `` in ``investigation.py``

Test with our existing evidence

You already have evidence such as:

```bash
Database connection pool exhausted

98 database connections active
out of maximum 100

Failed to execute checkout transaction

HTTP 500 returned to client```

So the Root Cause Agent receives:
```bash
Evidence 1
Database connection pool exhausted

Evidence 2
98 / 100 database connections

Evidence 3
Failed to execute checkout transaction

Evidence 4
HTTP 500 returned```

And should produce something conceptually like:

```bash
{
  "root_cause": "Database connection pool exhaustion",

  "explanation":
    "Checkout requests are failing because the database
     connection pool is nearly exhausted. Logs directly
     report pool exhaustion while metrics show 98 of 100
     connections in use.",

  "confidence": 0.94,

  "evidence_ids": [
    1,
    2,
    3
  ],

  "alternative_causes": [
    {
      "cause": "Database server overload",
      "reason_not_primary":
        "No direct evidence of database CPU or server
         resource exhaustion is currently available."
    }
  ],

  "uncertainty":
    "The evidence establishes connection pool saturation,
     but the underlying reason connections are not being
     released has not yet been identified."
}```

