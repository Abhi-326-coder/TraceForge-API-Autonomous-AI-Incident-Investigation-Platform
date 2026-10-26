
from app.observability.tracing import get_tracer


def test_tracer_can_create_span():
    tracer = get_tracer("traceforge.tests")

    with tracer.start_as_current_span("test-operation") as span:
        span.set_attribute("test.name", "tracing")

        assert span.is_recording()
