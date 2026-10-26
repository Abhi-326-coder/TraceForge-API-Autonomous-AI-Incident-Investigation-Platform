
from functools import lru_cache

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from app.config import settings


@lru_cache(maxsize=1)
def configure_tracing():
    resource = Resource.create({
        "service.name": "traceforge-api",
        "service.version": settings.app_version,
        "deployment.environment": (
            "development" if settings.debug else "production"
        ),
    })

    provider = TracerProvider(resource=resource)

    if settings.debug:
        # Local development: show spans in the backend console.
        provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter())
        )
    else:
        # Production: export spans to an OTLP-compatible collector.
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter())
        )

    trace.set_tracer_provider(provider)
    return provider


def get_tracer(name: str = "traceforge"):
    configure_tracing()
    return trace.get_tracer(name)
