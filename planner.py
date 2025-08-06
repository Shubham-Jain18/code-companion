import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import PLANNER_PROMPT

class Planner:
    """
    The Planner is responsible for interacting with the LLM to generate a
    step-by-step plan based on the user's request.
    """
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key) # type: ignore
        self.model = genai.GenerativeModel('gemini-2.0-flash') # type: ignore

    def generate_plan(self, history: list, user_request: str) -> dict:
        """Generates a plan by calling the Gemini API."""
        # For simplicity, we'll just format the history as a string for now.
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

        prompt = PLANNER_PROMPT.format(
            history=formatted_history,
            user_request=user_request
        )

        # Initialize response to None to prevent "PossiblyUnboundVariable" linter warning.
        response = None
        try:
            response = self.model.generate_content(prompt)
            
            # The response from the LLM might be wrapped in markdown backticks
            # We need to clean it to get the raw JSON string.
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            
            plan_json = json.loads(response_text)
            return plan_json

        except json.JSONDecodeError as e:
            # If JSON decoding fails, we still have the response object to log the raw text.
            response_text_for_error = response.text if response else "No response text available."
            print(f"Error: Failed to decode JSON from LLM response. Response was:\n{response_text_for_error}")
            return {"plan": [{"step": 1, "description": "Error handling response.", "tool_to_use": "final_answer", "parameters": {"answer": "I'm sorry, I had a problem understanding my own thoughts. Could you try rephrasing?"}}]}
        except Exception as e:
            print(f"An unexpected error occurred in the planner: {e}")
            return {"plan": [{"step": 1, "description": "Error handling response.", "tool_to_use": "final_answer", "parameters": {"answer": "I'm sorry, a critical error occurred."}}]}