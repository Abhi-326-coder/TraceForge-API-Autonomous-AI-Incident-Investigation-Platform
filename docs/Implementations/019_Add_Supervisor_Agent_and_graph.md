# Adding the Supervisor Agent and Creating a MultiAgent graph

## Supervisor Agent 

- Providint the Incident Details like below within the prompt and devise a plan returning a list of actions to be performed 

```python
    external_id: int
    title: str
    description: str
    service: str
    severity: str
```

- might return
```python
{
    plan:[logs, metrics, code]
}
```

- Next there is this ```route_after_supervisor``` which returns the nodes like "log_investigation" to be forwarded to perform action

```python
def route_after_supervisor(state):

    next_agent = state.get("next_agent")

    if next_agent == "logs":
        return "log_investigation"

    if next_agent == "metrics":
        return "metrics_investigation"

    if next_agent == "code":
        return "code_investigation"

    return "end"
```

-  ```advance_investigation_node``` updates the next_agent to be performed 

```python
def advance_investigation_node(state):

    plan = state.get(
        "investigation_plan",
        [],
    )

    current = state.get(
        "next_agent"
    )

    if current in plan:

        current_index = plan.index(
            current
        )

        next_index = current_index + 1

        if next_index < len(plan):

            return {
                "next_agent": plan[next_index],
            }

    return {
        "next_agent": None,
        "investigation_complete": True,
    }
```
- ```route_after_agent``` forwards the agent returned by the advance investigation 

```python
def route_after_agent(state):

    if state.get(
        "investigation_complete"
    ):
        return "end"

    next_agent = state.get(
        "next_agent"
    )

    if next_agent == "logs":
        return "log_investigation"

    if next_agent == "metrics":
        return "metrics_investigation"

    if next_agent == "code":
        return "code_investigation"

    return "end"
```


