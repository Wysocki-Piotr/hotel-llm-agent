import sys
import os
import pandas as pd
import asyncio
import time
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from src.agent.graph import build_agent_graph
from src.utils import setup_env, setup_logging
from src.core.database import init_db

# Konfiguracja
setup_env()
setup_logging()
init_db()

output_file = "data/evaluation_results_2.csv"


def extract_cost(text):
    """Próbuje wyciągnąć liczbę zmiennoprzecinkową z tekstu."""
    if not text: return None
    match = re.search(r"(\d+[.,]\d+)", text)
    if match:
        try:
            return float(match.group(1).replace(",", "."))
        except ValueError:
            return None
    return None


async def run_evaluation():
    try:
        df = pd.read_csv("data/dataset.csv")
        df = df.tail(23)
    except Exception as e:
        print(f"Błąd odczytu dataset.csv: {e}")
        return

    app = build_agent_graph()

    columns = [
        "id", "prompt",
        "expected_currency",  # Z datasetu, do porównania
        "agent_output",
        "extracted_cost",  # Cena z tekstu
        "extracted_city",  # Z argumentów search_hotels
        "extracted_num_nights",  # Z argumentów calculate_trip_cost
        "extracted_num_people",  # Z argumentów calculate_trip_cost
        "extracted_target_currency",  # Z argumentów get_exchange_rate
        "tools_used",  # Lista użytych narzędzi
        "error"
    ]

    # Inicjalizacja pliku CSV
    pd.DataFrame(columns=columns).to_csv(output_file, index=False)

    print(f"Rozpoczynam ewaluację na {len(df)} przykładach...")
    print(f"Wyniki są zapisywane na bieżąco do: {output_file}")

    for index, row in df.iterrows():
        prompt = row['prompt']
        # W dataset.csv kolumna nazywa się 'target_currency'
        expected_currency = row.get('target_currency', None)

        print(f"Processing ID {row['id']}...", end=" ", flush=True)

        inputs = {
            "messages": [HumanMessage(content=prompt)],
            "plan": "",
            "logs": [],
            "mode": "chat"  # Domyślny tryb
        }

        final_output = ""
        is_error = False

        # Zmienne do ekstrakcji parametrów (domyślnie None)
        extracted_params = {
            "city": None,
            "nights": None,
            "people": None,
            "currency": None
        }
        tool_names = []

        try:
            # Uruchomienie agenta
            output = await app.ainvoke(inputs)
            final_msg = output["messages"][-1]
            final_output = final_msg.content

            # Analiza historii wiadomości pod kątem użytych narzędzi i ich argumentów
            if "messages" in output:
                for msg in output["messages"]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool in msg.tool_calls:
                            name = tool["name"]
                            args = tool["args"]  # To jest słownik argumentów

                            # Zbieramy nazwę narzędzia
                            tool_names.append(name)

                            # Ekstrakcja parametrów zależnie od narzędzia
                            # Nadpisujemy wartości, biorąc pod uwagę ostatnie skuteczne wywołanie (lub pierwsze, zależy od logiki - tu bierzemy każde kolejne)

                            if name == "search_hotels":
                                # Szukamy argumentu 'city'
                                if "city" in args:
                                    extracted_params["city"] = args["city"]

                            elif name == "calculate_trip_cost":
                                # Szukamy 'nights' i 'people'
                                if "nights" in args:
                                    extracted_params["nights"] = args["nights"]
                                if "people" in args:
                                    extracted_params["people"] = args["people"]

                            elif name == "get_exchange_rate":
                                # Szukamy 'target_currency'
                                if "target_currency" in args:
                                    extracted_params["currency"] = args["target_currency"]

            print("OK.")

        except Exception as e:
            final_output = f"ERROR: {str(e)}"
            is_error = True
            print("FAIL.")

        # Próba wyciągnięcia ceny z tekstu (jako dodatek)
        extracted_cost = extract_cost(final_output)

        # Przygotowanie wiersza wyników
        single_result = pd.DataFrame([{
            "id": row['id'],
            "prompt": prompt,
            "expected_currency": expected_currency,
            "agent_output": final_output,
            "extracted_cost": extracted_cost,
            "extracted_city": extracted_params["city"],
            "extracted_num_nights": extracted_params["nights"],
            "extracted_num_people": extracted_params["people"],
            "extracted_target_currency": extracted_params["currency"],

            "tools_used": str(tool_names),
            "error": is_error
        }])

        # Zapis do pliku
        single_result.to_csv(output_file, mode='a', header=False, index=False)

        # Opóźnienie (Rate Limit protection)
        time.sleep(10)

    print(f"\n Ewaluacja zakończona. Pełne wyniki w {output_file}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())