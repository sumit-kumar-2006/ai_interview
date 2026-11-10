import os
import pytest

# Configure testing environment by default during automated test execution
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("ALLOW_LEGACY_SCORING", "true")
os.environ.setdefault("ALLOW_TEST_FALLBACK", "true")

