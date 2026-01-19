import pandas as pd
import numpy as np
import os

# Konfiguracja ścieżek
DATASET_PATH = "data/dataset.csv"
RESULTS_PART1_PATH = "data/evaluation_results.csv"
RESULTS_PART2_PATH = "data/results_2.csv"

# Słownik mapujący polskie nazwy miast na angielskie
CITY_MAPPING = {
    "warszawa": "warsaw",
    "rzym": "rome",
    "paryż": "paris",
    "londyn": "london",
    "nowy jork": "new york",
    "barcelona": "barcelona",
    "tokio": "tokyo",
    "berlin": "berlin",
    "sydney": "sydney",
    "radom": "radom"
}


def normalize_city_name(city_val):
    """Pomocnicza funkcja do normalizacji nazwy miasta."""
    if pd.isna(city_val):
        return None
    clean_city = str(city_val).strip().lower()
    return CITY_MAPPING.get(clean_city, clean_city)


def check_numeric(row, col_expected, col_extracted):
    """
    Sprawdza równość liczbową dla nocy i osób.
    ZASADA: None == None -> 1
    ZASADA: None == 0 -> 1
    ZASADA: 0 == None -> 1
    """
    val_exp = row[col_expected]
    val_ext = row[col_extracted]

    # Konwersja na float, zamieniając None/NaN na 0.0
    num_exp = 0.0 if pd.isna(val_exp) else float(val_exp)
    num_ext = 0.0 if pd.isna(val_ext) else float(val_ext)

    # Porównanie z tolerancją
    return 1 if abs(num_exp - num_ext) < 0.001 else 0


def check_currency(row, col_expected, col_extracted):
    """
    Sprawdza walutę.
    ZASADA: None == None -> 1
    ZASADA: None == PLN -> 1 (Domyślna waluta to PLN)
    """
    val_exp = row[col_expected]
    val_ext = row[col_extracted]

    # Normalizacja: None/NaN zamieniamy na "PLN", resztę uppercase
    curr_exp = "PLN" if pd.isna(val_exp) else str(val_exp).strip().upper()
    curr_ext = "PLN" if pd.isna(val_ext) else str(val_ext).strip().upper()

    return 1 if curr_exp == curr_ext else 0


def check_city(row, col_expected, col_extracted):
    """
    Sprawdza miasto.
    ZASADA: None == None -> 1
    Inne: Case insensitive + mapping
    """
    val_exp = row[col_expected]
    val_ext = row[col_extracted]

    # Jeśli oba są puste -> 1
    if pd.isna(val_exp) and pd.isna(val_ext):
        return 1

    # Jeśli tylko jeden jest pusty -> 0
    if pd.isna(val_exp) or pd.isna(val_ext):
        return 0

    norm_exp = normalize_city_name(val_exp)
    norm_ext = normalize_city_name(val_ext)

    return 1 if norm_exp == norm_ext else 0


def generate_detailed_report():
    """Wczytuje dataset i oba pliki wyników, łączy je i ocenia."""

    # 1. Wczytanie Datasetu
    if not os.path.exists(DATASET_PATH):
        print(f"Błąd: Nie znaleziono pliku {DATASET_PATH}")
        return None
    df_dataset = pd.read_csv(DATASET_PATH)

    # 2. Wczytanie i łączenie wyników (Concatenate)
    results_frames = []

    if os.path.exists(RESULTS_PART1_PATH):
        print(f"Wczytuję: {RESULTS_PART1_PATH}")
        results_frames.append(pd.read_csv(RESULTS_PART1_PATH))
    else:
        print(f"Ostrzeżenie: Brak pliku {RESULTS_PART1_PATH}")

    if os.path.exists(RESULTS_PART2_PATH):
        print(f"Wczytuję: {RESULTS_PART2_PATH}")
        results_frames.append(pd.read_csv(RESULTS_PART2_PATH))
    else:
        print(f"Ostrzeżenie: Brak pliku {RESULTS_PART2_PATH}")

    if not results_frames:
        print("Błąd: Nie znaleziono żadnych plików z wynikami.")
        return None

    # Łączenie ramek (jeden pod drugim)
    df_results = pd.concat(results_frames, ignore_index=True)

    # Opcjonalnie: usunięcie duplikatów po ID, jeśli np. coś się nadpisało
    df_results.drop_duplicates(subset=['id'], keep='last', inplace=True)

    print(f"Łącznie wczytano {len(df_results)} wierszy wyników.")

    # 3. Merge z Datasetem (po ID)
    merged = pd.merge(
        df_dataset,
        df_results,
        on="id",
        how="inner",
        suffixes=('', '_extracted')
    )

    detailed_df = pd.DataFrame()
    detailed_df['id'] = merged['id']
    detailed_df['prompt'] = merged['prompt']

    # 4. Aplikowanie logiki porównań

    detailed_df['correct_city'] = merged.apply(
        lambda row: check_city(row, 'city', 'extracted_city'), axis=1
    )

    detailed_df['correct_num_nights'] = merged.apply(
        lambda row: check_numeric(row, 'num_nights', 'extracted_num_nights'), axis=1
    )

    detailed_df['correct_num_people'] = merged.apply(
        lambda row: check_numeric(row, 'num_people', 'extracted_num_people'), axis=1
    )

    detailed_df['correct_currency'] = merged.apply(
        lambda row: check_currency(row, 'target_currency', 'extracted_target_currency'), axis=1
    )

    return detailed_df


def metrics(detailed_df):
    """Liczy Accuracy (średnia z kolumn 0/1)."""
    if detailed_df is None or detailed_df.empty:
        return {}

    cols = ['correct_currency', 'correct_num_nights', 'correct_num_people', 'correct_city']
    stats = {}

    for col in cols:
        if col in detailed_df.columns:
            stats[col] = detailed_df[col].mean()

    return stats


if __name__ == "__main__":
    df_det = generate_detailed_report()

    if df_det is not None:
        print("\n=== PRÓBKA RAPORTU SZCZEGÓŁOWEGO ===")
        print(df_det.head())

        output_path = "data/evaluation_metrics_detailed.csv"
        df_det.to_csv(output_path, index=False)
        print(f"\nZapisano szczegóły do: {output_path}")

        print("\n=== WYNIKI METRYK (ACCURACY) ===")
        results = metrics(df_det)
        for k, v in results.items():
            print(f"{k}: {v:.2%}")