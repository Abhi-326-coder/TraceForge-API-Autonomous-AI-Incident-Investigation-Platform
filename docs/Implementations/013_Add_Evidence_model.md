## Add the Evidence Model 

```python
class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    investigation: Mapped["Investigation"] = relationship(
        back_populates="evidence",
    )
```

```bash
Incident
   │
   ▼
Investigation
   │
   ├── Evidence #1
   ├── Evidence #2
   ├── Evidence #3
   └── Evidence #4
```

12.4 Why source_type and provider?

Again, this distinction matters.

Suppose:
```json
{
  "source_type": "logs",
  "provider": "loki"
}```

versus:
```json
{
  "source_type": "logs",
  "provider": "simulator"
}```

Both are logs.

But they came from different systems.

Similarly:
```json
{
  "source_type": "metrics",
  "provider": "prometheus"
}```

or:
```json
{
  "source_type": "code",
  "provider": "github"
}```

This makes evidence provider-independent.