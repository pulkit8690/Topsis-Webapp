import os
import cohere
from dotenv import load_dotenv
import ast

load_dotenv()
DEFAULT_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(DEFAULT_API_KEY)

def generate_serpapi_prompts(alternatives, criteria, api_key=None):
    """
    Generates clean, domain-agnostic search queries using Cohere (Command R+).
    Each [alternative, criterion] pair becomes a Google-style query.
    Example outputs:
    - "Battery life of iPhone 15"
    - "Tuition fee of Stanford University in INR"
    """

    prompt = (
        "You're an assistant that helps generate search queries for looking up information on the web.\n"
        "Given a list of items (called alternatives) and a list of decision criteria, create one Google-style "
        "search query per [alternative, criterion] pair.\n\n"
        "Your job is to generate very specific and realistic search queries that help retrieve numeric or factual data.\n"
        "Include units or context where applicable (e.g., 'in INR', 'in km/l', 'in 2024', 'according to QS Ranking').\n"
        "Return only a valid Python list of strings.\n\n"
        f"Alternatives: {alternatives}\nCriteria: {criteria}\n\n"
        "Search Query List:"
    )

    try:
        response = co.chat(
            model="command-r-plus",
            message=prompt,
            temperature=0.3
        )

        result = response.text.strip()

        # Safely parse result into a Python list
        if result.startswith("["):
            return ast.literal_eval(result)
        else:
            return [line.strip("- ").strip() for line in result.split("\n") if line.strip()]

    except Exception as e:
        print(f"[ERROR] Failed to generate prompts from Cohere: {e}")
        return []
