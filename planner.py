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

    def __init__(self, context_manager=None):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        genai.configure(api_key=api_key)  # type: ignore
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore
        self.context_manager = context_manager

    def _format_history(self, history: list) -> str:
        """
        Helper: Converts the list of message dicts into a clean string for the LLM.
        Fixes the 'Double Thinking' bug by making observations explicit.
        """
        formatted_lines = []
        for msg in history:
            role = msg.get('role')
            content = msg.get('content')
            tool = msg.get('tool_used')

            if role == "user":
                formatted_lines.append(f"User: {content}")
            elif role == "assistant":
                formatted_lines.append(f"Assistant: {content}")
            elif role == "observation":
                # CRITICAL FIX: Clearly label observations so the LLM knows the action is done.
                source = f" (from tool '{tool}')" if tool else ""
                formatted_lines.append(f"Observation{source}: {content}")
            else:
                formatted_lines.append(f"{role}: {content}")

        return "\n\n".join(formatted_lines)

    def generate_plan(self, history: list, user_request: str) -> dict:
        """
        Generates a plan by calling the Gemini API.
        Returns a dictionary containing the conversational preamble and the plan.
        Gemini gets our custom prompt, conversation history and user request
        """
        # 1. Format the history list into a string using the helper
        formatted_history = self._format_history(history)

        # 2. Retrieve File Context (if available)
        context_summary = "No files loaded in context."
        if self.context_manager:
            context_summary = self.context_manager.get_context()

        # 3. Format the Prompt
        # Ensure your PLANNER_PROMPT in prompts.py has the {context_summary} placeholder!
        prompt = PLANNER_PROMPT.format(
            history=formatted_history,
            user_request=user_request,
            context_summary=context_summary
        )

        response = None
        try:
            # 4. Call Gemini with Native JSON Mode (More robust than regex parsing)
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Parse the JSON response directly
            response_json = json.loads(response.text)

            return {
                "preamble": response_json.get("preamble", ""),
                "plan": response_json.get("plan", [])
            }

        except Exception as e:
            print(f"An unexpected error occurred in the planner: {e}")
            # Return a safe fallback so the agent doesn't crash
            return {
                "preamble": f"I encountered an error: {str(e)}",
                "plan": []
            }
