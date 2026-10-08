## Setup the Nextjs and add the types, components, lib and types 

### Adding the Investigation types :

```typescript
export type InvestigationEvent = {
  event_type: string;
  investigation_id: number;
  message: string;
  agent?: string | null;
  data: Record<string, unknown>;
  timestamp: string;
};

export type Evidence = {
  id: number;
  source_type: string;
  provider: string;
  title: string;
  content: string;
  source_reference?: string | null;
};

export type RootCause = {
  root_cause: string;
  explanation: string;
  confidence: number;
  evidence_ids: number[];
  alternative_causes: {
    cause: string;
    reason_not_primary: string;
  }[];
  uncertainty: string;
};
```

### In lib folder adding the api and sse route calling function 

- getIncident: which will call the /api/incidents/{incident_id} fetching the Incident details by the Incident Id

- startInvestigation: which calls POST /api/incidents/${incidentId}/investigate starting the investigation

- In the sse.ts we have ``connectInvestigationEvents`` which listens the response comming from Streaming response from /api/investigations/${investigationId}/events

### Adding the Components of Investigation : 
- EvidencePanel
- IncidentHeader
- InvestigationtimeLine
- RootCauseCard

### Adding the Pages of Home and page of the Incident 

- http://localhost:3000/

- http://localhost:3000/incident/1 (This one still has some issue with calling the getIncident api will be fixed later)