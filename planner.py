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
        self.model = genai.GenerativeModel('gemini-3-pro-preview') # type: ignore

    def generate_plan(self, history: list, user_request: str) -> dict:
        """
        Generates a plan by calling the Gemini API.
        Returns a dictionary containing the conversational preamble and the plan.
        """
        formatted_history = "\n".join([f"Role: {msg['role']}, Content: {msg['content']}" for msg in history])

        prompt = PLANNER_PROMPT.format(
            history=formatted_history,
            user_request=user_request
        )

        response = None
        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text
            
            preamble = ""
            plan_json = None

            json_start = raw_text.find("```json")
            if json_start != -1:
                preamble = raw_text[:json_start].strip()
                json_end = raw_text.rfind("```")
                json_str = raw_text[json_start + 7 : json_end].strip()
                plan_json = json.loads(json_str)
            else:
                # Fallback if no JSON block is found
                preamble = "I had a thought, but couldn't formulate a clear plan."
                plan_json = {"plan": [{"step": 1, "description": "Provide a fallback answer.", "tool_to_use": "final_answer", "parameters": {"answer": "I'm sorry, I'm a bit confused. Could you clarify?"}}]}

            return {"preamble": preamble, "plan": plan_json.get("plan", [])}

        except json.JSONDecodeError as e:
            response_text_for_error = response.text if response else "No response text available."
            print(f"Error: Failed to decode JSON from LLM response. Response was:\n{response_text_for_error}")
            return {"preamble": "I'm sorry, I had a problem understanding my own thoughts.", "plan": []}
        except Exception as e:
            print(f"An unexpected error occurred in the planner: {e}")
            return {"preamble": "I'm sorry, a critical error occurred.", "plan": []}
