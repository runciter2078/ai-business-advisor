"""
Tests del generador de datos sintéticos.

Verifica que el dataset generado tiene las propiedades estadísticas correctas
para que el pipeline de forecasting lo pueda procesar.
"""

import pandas as pd
import pytest

from data.generate_sample import generate_sales_data


@pytest.fixture(scope="module")
def df():
    return generate_sales_data(start_date="2024-01-01", years=2, seed=42)


class TestDataShape:
    def test_has_expected_columns(self, df):
        assert set(["date", "sales", "weekday", "is_holiday"]).issubset(df.columns)

    def test_row_count_two_years(self, df):
        # 2024 es bisiesto: 366 + 365 = 731 días
        assert len(df) in (730, 731)

    def test_no_null_values(self, df):
        assert df.isnull().sum().sum() == 0

    def test_no_negative_sales(self, df):
        assert (df["sales"] >= 0).all()

    def test_sales_range_realistic(self, df):
        """Las ventas deben estar en el rango esperado para hostelería."""
        assert df["sales"].min() > 100
        assert df["sales"].max() < 5000

    def test_weekday_valid_range(self, df):
        assert df["weekday"].between(0, 6).all()

    def test_is_holiday_binary(self, df):
        assert df["is_holiday"].isin([0, 1]).all()


class TestSeasonality:
    def test_friday_saturday_higher_than_monday(self, df):
        """La estacionalidad semanal debe ser visible en los datos."""
        df["dow"] = pd.to_datetime(df["date"]).dt.dayofweek
        monday_mean = df[df["dow"] == 0]["sales"].mean()
        friday_mean = df[df["dow"] == 4]["sales"].mean()
        saturday_mean = df[df["dow"] == 5]["sales"].mean()

        assert friday_mean > monday_mean * 1.2
        assert saturday_mean > monday_mean * 1.2

    def test_summer_higher_than_january(self, df):
        """La estacionalidad anual debe ser visible."""
        df["month"] = pd.to_datetime(df["date"]).dt.month
        january_mean = df[df["month"] == 1]["sales"].mean()
        august_mean = df[df["month"] == 8]["sales"].mean()

        assert august_mean > january_mean * 1.1

    def test_holidays_not_zero(self, df):
        """Los festivos deben tener ventas (son buenos días en hostelería)."""
        holiday_sales = df[df["is_holiday"] == 1]["sales"]
        assert len(holiday_sales) > 0
        assert (holiday_sales > 0).all()

    def test_reproducibility(self):
        """El mismo seed debe producir el mismo dataset."""
        df1 = generate_sales_data(seed=42)
        df2 = generate_sales_data(seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seeds_differ(self):
        df1 = generate_sales_data(seed=42)
        df2 = generate_sales_data(seed=99)
        assert not df1["sales"].equals(df2["sales"])
