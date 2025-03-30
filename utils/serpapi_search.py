import requests
import os
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_and_extract_value(query, serpapi_key=None):
    """
    Performs a real-time Google search using SerpAPI and returns the raw factual value/text.
    """
    key = serpapi_key or SERPAPI_KEY
    if not key:
        raise ValueError("SerpAPI key not provided")

    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": key
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        # 1. Check answer box
        if 'answer_box' in data:
            answer_box = data['answer_box']
            if 'answer' in answer_box:
                return answer_box['answer']
            if 'snippet' in answer_box:
                return answer_box['snippet']
            if 'snippet_highlighted_words' in answer_box:
                return answer_box['snippet_highlighted_words'][0]

        # 2. Knowledge Graph fallback
        if 'knowledge_graph' in data:
            kg = data['knowledge_graph']
            for value in kg.values():
                if isinstance(value, str):
                    return value

        # 3. Organic result snippet fallback
        if 'organic_results' in data and len(data['organic_results']) > 0:
            snippet = data['organic_results'][0].get('snippet', '')
            if snippet:
                return snippet

        return "N/A"

    except Exception as e:
        print(f"[ERROR] SerpAPI request failed: {e}")
        return "N/A"
