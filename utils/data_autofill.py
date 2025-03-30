from utils.prompt_generator import generate_serpapi_prompts
from utils.serpapi_search import search_and_extract_value
from utils.cohere_extractor import extract_numeric_with_cohere
import pandas as pd
import time

def autofill_criteria_values(alternatives, criteria, openai_api_key=None, serpapi_key=None, delay=1.0):
    """
    Main function to autofill a TOPSIS-compatible DataFrame using:
    - ChatGPT to generate search prompts
    - SerpAPI to fetch real values
    - OpenAI GPT to extract numeric values
    - Returns a DataFrame with alternatives as rows, criteria as columns
    """
    print("[INFO] Generating search prompts using ChatGPT...")
    search_prompts = generate_serpapi_prompts(alternatives, criteria, api_key=openai_api_key)

    # Initialize DataFrame structure
    filled_data = { "Alternative": alternatives }
    for criterion in criteria:
        filled_data[criterion] = []

    print("[INFO] Starting data collection using SerpAPI + GPT...")
    for alt in alternatives:
        for criterion in criteria:
            # Match best query from generated prompts
            prompt = f"{criterion} of {alt}"
            matched_prompt = next((p for p in search_prompts if alt in p and criterion.lower() in p.lower()), prompt)

            print(f"🔍 Searching: {matched_prompt}")
            raw_text = search_and_extract_value(matched_prompt, serpapi_key=serpapi_key)
            print(f"🌐 Raw result: {raw_text}")

            numeric_value = extract_numeric_with_cohere(raw_text, alt)
            print(f"🧠 Numeric value: {numeric_value}")

            filled_data[criterion].append(numeric_value)
            time.sleep(delay)

    df = pd.DataFrame(filled_data)
    print("[✅] Autofill complete. Returning cleaned DataFrame.")
    return df
