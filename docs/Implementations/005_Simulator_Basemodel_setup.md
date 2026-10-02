# Add the routes required for the project

- first created the simulator to understand the requirements and pydantic schemas

- In the simulator we have the files which return the incidents, logs and metrics 



```python
class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    service: str
    severity: str
    status: str
```
```python
class LogResponse(BaseModel):
    timestamp: str
    service: str
    level: str
    message: str
```
```python
class MetricsResponse(BaseModel):
    request_rate: int
    error_rate: float
    latency_ms: int
    database_connections: int
    database_connection_limit: int
```