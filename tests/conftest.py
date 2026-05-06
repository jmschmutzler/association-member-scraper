import os
import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_jobs():
    import jobs as jobs_module
    jobs_module._jobs.clear()
    yield
    jobs_module._jobs.clear()
