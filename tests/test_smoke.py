"""Smoke tests for MRP pipeline modules."""

from mrp.calendar import generate_calendar_horizon


def test_calendar_horizon_length():
    cal = generate_calendar_horizon()
    assert len(cal) == 24


def test_calendar_horizon_format():
    cal = generate_calendar_horizon(start_date="2026-06-01")
    assert cal[0] == "2026-06"
    assert cal[-1] == "2028-05"
