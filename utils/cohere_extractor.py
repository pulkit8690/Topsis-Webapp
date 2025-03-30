import os
import re
import numpy as np
import cohere
from dotenv import load_dotenv

load_dotenv()
DEFAULT_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(DEFAULT_API_KEY)

def fallback_extract_number(text):
    """
    Regex fallback: extract first numeric value from a string (int or float).
    """
    if not text:
        return np.nan
    text = re.sub(r'[₹$,€£]', '', text)  # Strip symbols
    match = re.search(r'\d+(?:\.\d+)?', text)
    return float(match.group()) if match else np.nan


def extract_numeric_with_cohere(raw_text, alternative_name=""):
    """
    Uses Cohere to extract the most relevant numeric value from a string.
    Optimized prompt includes the alternative name for better grounding.
    """
    if not raw_text or raw_text.lower() in ["n/a", "none", ""]:
        return np.nan

    try:
        prompt = (
            f"Extract the numeric value from the result for '{alternative_name}'.\n"
            f"The sentence is:\n\n{raw_text}\n\n"
            f"Return only the number without units or symbols. If no number is found, return 'NaN'."
        )

        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.2
        )

        result = response.text.strip()

        if result.lower() == "nan":
            raise ValueError("Cohere returned 'NaN'")

        # Extract numeric part from response
        match = re.search(r'\d+(?:\.\d+)?', result)
        if match:
            return float(match.group())

        raise ValueError("No numeric value found")

    except Exception as e:
        print(f"[WARN] Cohere failed. Using fallback. Reason: {e}")
        return fallback_extract_number(raw_text)
