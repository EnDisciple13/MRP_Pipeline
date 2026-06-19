"""Calendar horizon utilities."""

import pandas as pd


def generate_calendar_horizon(start_date="2026-06-01", periods=24):
    """Generates the absolute string array for the X-axis."""
    dates = pd.date_range(start=start_date, periods=periods, freq="MS")
    return [date.strftime("%Y-%m") for date in dates]


def advance_rolling_horizon(alpha_calendar_array):
    """
    Drops the month that just passed and calculates the next month
    to maintain the 24-period horizon.
    """
    print("Executing Time Shift: Rolling Calendar Forward...")
    last_month = pd.to_datetime(alpha_calendar_array[-1])
    next_month = last_month + pd.DateOffset(months=1)
    return alpha_calendar_array[1:] + [next_month.strftime("%Y-%m")]
