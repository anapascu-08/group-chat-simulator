from config import get_delay_range_seconds


def test_default_delay_range_is_short_for_dev():
    assert get_delay_range_seconds() == (0.5, 1.5)


def test_delay_range_reads_env_vars(monkeypatch):
    monkeypatch.setenv("RESPONSE_DELAY_MIN_S", "120")
    monkeypatch.setenv("RESPONSE_DELAY_MAX_S", "480")

    assert get_delay_range_seconds() == (120.0, 480.0)
