
import os

import streamlit as st
from google import genai


MODEL_NAME = "gemma-4-26b-a4b-it"


def get_api_key():
    """Read the Google API key securely."""

    key = os.getenv("GEMINI_API_KEY", "")

    try:
        key = st.secrets.get("GEMINI_API_KEY", key)
    except Exception:
        pass

    return key


def generate_saving_strategies(expense_summary, total, budget):
    """Generate personalized expense-management advice."""

    api_key = get_api_key()

    if not api_key:
        return (
            "Google API key is missing. Add GEMINI_API_KEY "
            "to .streamlit/secrets.toml."
        )

    remaining = budget - total

    prompt = f"""
    You are a practical personal expense management assistant.

    Currency: Pakistani Rupees (PKR)

    Monthly spending by category:
    {expense_summary}

    Total spending: Rs. {total:.2f}
    Monthly budget: Rs. {budget:.2f}
    Budget remaining: Rs. {remaining:.2f}

    Provide:
    1. A brief spending assessment.
    2. Three practical ways to manage expenses.
    3. One category to review for possible savings,
       only when supported by the provided data.
    4. One actionable next step.

    Rules:
    - Base advice only on the supplied figures.
    - Do not invent income or expenses.
    - Do not suggest reducing essential healthcare.
    - Keep the response concise and easy to understand.
    - Use clear headings and bullet points.
    """

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            return "The AI returned an empty response. Please try again."

        return response.text

    except Exception as error:
        # Avoid exposing API keys or detailed internal error messages.
        st.error(
            f"AI request failed ({type(error).__name__}). "
            "Check your API key, model availability, "
            "internet connection, and usage limits."
        )
        return None
