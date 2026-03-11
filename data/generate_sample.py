"""
Generador de datos sintéticos de ventas diarias para hostelería.

Genera 2 años de datos con:
  - Estacionalidad semanal realista (viernes/sábado +40%)
  - Estacionalidad anual (verano, Navidad, Semana Santa)
  - Festivos nacionales con impacto diferenciado
  - Ruido gaussiano multiplicativo controlado
  - Rango de ventas 200-2000€/día (restaurante mediano)

Uso:
    python data/generate_sample.py
    python data/generate_sample.py --output data/mi_dataset.csv
    python data/generate_sample.py --years 3 --seed 99
"""

import argparse
import os

import numpy as np
import pandas as pd


# =============================================================================
# Festivos nacionales España — solo los de mayor impacto en hostelería
# =============================================================================

SPANISH_HOLIDAYS = {
    # 2024
    "2024-01-01", "2024-01-06",
    "2024-03-28", "2024-03-29",  # Semana Santa
    "2024-05-01", "2024-08-15",
    "2024-10-12", "2024-11-01",
    "2024-12-06", "2024-12-08",
    "2024-12-24", "2024-12-25", "2024-12-31",
    # 2025
    "2025-01-01", "2025-01-06",
    "2025-04-17", "2025-04-18",  # Semana Santa
    "2025-05-01", "2025-08-15",
    "2025-10-12", "2025-11-01",
    "2025-12-06", "2025-12-08",
    "2025-12-24", "2025-12-25", "2025-12-31",
    # 2026
    "2026-01-01", "2026-01-06",
    "2026-04-02", "2026-04-03",  # Semana Santa
    "2026-05-01", "2026-08-15",
    "2026-10-12", "2026-11-01",
    "2026-12-06", "2026-12-08",
    "2026-12-24", "2026-12-25", "2026-12-31",
}


def _weekly_factor(dayofweek: int) -> float:
    """
    Factor multiplicativo según día de la semana.
    Lunes=0, Domingo=6. Basado en datos reales de sector hostelería España.
    """
    factors = {
        0: 0.72,  # Lunes — día flojo
        1: 0.75,  # Martes
        2: 0.82,  # Miércoles
        3: 0.88,  # Jueves
        4: 1.25,  # Viernes — repunte claro
        5: 1.45,  # Sábado — pico semanal
        6: 1.13,  # Domingo — comidas en familia
    }
    return factors[dayofweek]


def _annual_factor(month: int, day: int) -> float:
    """
    Factor multiplicativo por época del año.
    Incorpora picos de verano y Navidad, bache de enero-febrero.
    """
    # Bache enero-febrero (post fiestas, frío, dietas de enero)
    if month in (1, 2):
        return 0.80

    # Semana Santa variable en marzo-abril: se maneja como festivo
    if month == 3:
        return 0.92

    # Primavera suave
    if month == 4:
        return 1.02

    if month == 5:
        return 1.05

    # Junio: inicio de calor, terrazas
    if month == 6:
        return 1.15

    # Julio-Agosto: pico veraniego
    if month in (7, 8):
        return 1.35

    # Septiembre: vuelta, correcta
    if month == 9:
        return 1.05

    # Octubre: temporada estable
    if month == 10:
        return 0.98

    # Noviembre: bache otoñal
    if month == 11:
        return 0.90

    # Diciembre: Navidad
    if month == 12:
        if day >= 20:
            return 1.50   # Fiestas navideñas — pico absoluto
        return 1.10

    return 1.0


def _holiday_factor(date: pd.Timestamp, holiday_set: set) -> float:
    """
    Factor para festivos. Los festivos en hostelería no bajan ventas —
    suben porque la gente sale. Pero el día anterior al festivo baja.
    """
    date_str = date.strftime("%Y-%m-%d")
    next_day = (date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    if date_str in holiday_set:
        return 1.30   # Festivo: sube
    if next_day in holiday_set and date.dayofweek not in (5, 6):
        return 0.88   # Víspera de festivo entre semana: baja un poco
    return 1.0


def generate_sales_data(
    start_date: str = "2024-01-01",
    years: int = 2,
    base_sales: float = 850.0,
    noise_level: float = 0.10,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Genera un DataFrame con ventas diarias sintéticas de hostelería.

    Modelo generativo:
        sales(t) = base * f_weekly(t) * f_annual(t) * f_holiday(t) * ε(t)

    Donde ε(t) ~ LogNormal(0, noise_level) para ruido multiplicativo
    (asimetría positiva realista: outliers de días buenos, no días negativos).

    Args:
        start_date: Fecha de inicio en formato YYYY-MM-DD
        years:      Número de años a generar
        base_sales: Ventas base diarias en euros (media de un lunes normal)
        noise_level: Desviación estándar del ruido log-normal
        seed:       Semilla para reproducibilidad

    Returns:
        DataFrame con columnas [date, sales, weekday, is_holiday]
    """
    rng = np.random.default_rng(seed)

    start = pd.Timestamp(start_date)
    end = start + pd.DateOffset(years=years) - pd.Timedelta(days=1)
    dates = pd.date_range(start=start, end=end, freq="D")

    holiday_set = SPANISH_HOLIDAYS

    records = []
    for date in dates:
        w_factor = _weekly_factor(date.dayofweek)
        a_factor = _annual_factor(date.month, date.day)
        h_factor = _holiday_factor(date, holiday_set)

        # Ruido multiplicativo log-normal: media 1, sin ventas negativas
        noise = rng.lognormal(mean=0.0, sigma=noise_level)

        raw_sales = base_sales * w_factor * a_factor * h_factor * noise

        # Redondear a 2 decimales (euros)
        sales = round(float(np.clip(raw_sales, 0.0, None)), 2)

        is_holiday = int(date.strftime("%Y-%m-%d") in holiday_set)

        records.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "sales": sales,
                "weekday": date.dayofweek,
                "is_holiday": is_holiday,
            }
        )

    df = pd.DataFrame(records)

    return df


def print_stats(df: pd.DataFrame) -> None:
    """Imprime estadísticas descriptivas del dataset generado."""
    print("\n" + "=" * 60)
    print("DATASET SINTÉTICO — ESTADÍSTICAS")
    print("=" * 60)
    print(f"  Filas:          {len(df):,}")
    print(f"  Período:        {df['date'].min()} → {df['date'].max()}")
    print(f"  Ventas media:   {df['sales'].mean():,.0f}€/día")
    print(f"  Ventas mediana: {df['sales'].median():,.0f}€/día")
    print(f"  Ventas std:     {df['sales'].std():,.0f}€")
    print(f"  Ventas min:     {df['sales'].min():,.0f}€")
    print(f"  Ventas max:     {df['sales'].max():,.0f}€")
    print(f"  Festivos:       {df['is_holiday'].sum()} días")
    print()

    print("  Media por día de semana:")
    dow_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    by_dow = df.groupby("weekday")["sales"].mean()
    for dow, mean_sales in by_dow.items():
        bar = "█" * int(mean_sales / 50)
        print(f"    {dow_names[dow]}: {mean_sales:,.0f}€  {bar}")

    print()
    print("  Media por mes:")
    df["month"] = pd.to_datetime(df["date"]).dt.month
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    by_month = df.groupby("month")["sales"].mean()
    for month, mean_sales in by_month.items():
        bar = "█" * int(mean_sales / 60)
        print(f"    {month_names[month - 1]}: {mean_sales:,.0f}€  {bar}")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Genera datos sintéticos de ventas diarias para hostelería."
    )
    parser.add_argument(
        "--output",
        default="data/sample_data.csv",
        help="Ruta de salida del CSV (default: data/sample_data.csv)",
    )
    parser.add_argument(
        "--start-date",
        default="2024-01-01",
        help="Fecha de inicio YYYY-MM-DD (default: 2024-01-01)",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=2,
        help="Número de años a generar (default: 2)",
    )
    parser.add_argument(
        "--base-sales",
        type=float,
        default=850.0,
        help="Ventas base en euros/día para un lunes normal (default: 850)",
    )
    parser.add_argument(
        "--noise",
        type=float,
        default=0.10,
        help="Nivel de ruido log-normal 0.0-1.0 (default: 0.10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla aleatoria para reproducibilidad (default: 42)",
    )
    args = parser.parse_args()

    print(f"Generando {args.years} año(s) de datos desde {args.start_date}...")

    df = generate_sales_data(
        start_date=args.start_date,
        years=args.years,
        base_sales=args.base_sales,
        noise_level=args.noise,
        seed=args.seed,
    )

    print_stats(df)

    # Guardar solo date y sales en el CSV de demo (weekday e is_holiday
    # los deriva el pipeline automáticamente — tal como especifica el doc maestro)
    output_cols = ["date", "sales", "weekday", "is_holiday"]
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    df[output_cols].to_csv(args.output, index=False)

    print(f"✓ CSV guardado en: {args.output}")
    print(f"  Columnas: {', '.join(output_cols)}")
    print(f"  Nota: 'weekday' e 'is_holiday' son opcionales en el API —")
    print(f"        el pipeline las deriva si no se incluyen.\n")


if __name__ == "__main__":
    main()
