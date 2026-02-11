from planner import Planner
from executor import Executor
from state_manager import StateManager
from context.context_manager import ContextManager


def main():
    """
    The main orchestrator loop for the AI Code Companion.
    Refactored to use a ReAct (Reason-Act-Observe) loop.
    """

    state_manager = StateManager()
    context_manager = ContextManager()
    planner = Planner(context_manager=context_manager)
    executor = Executor(context_manager=context_manager)

    session_id = state_manager.create_new_session()

    print("="*50)
    print("AI Code Companion - ReAct Mode")
    print(f"Session ID: {session_id}")
    print("Type 'exit' to end.")
    print("="*50)

    while True:
        user_request = input("You: ")
        if user_request.lower() == 'exit':
            print("Assistant: Goodbye.")
            break

        # Save user message
        state_manager.add_message(
            session_id=session_id, role="user", content=user_request)

        step_count = 0
        max_steps = 15  # Safety limit to prevent infinite loops

        # --- AGENT LOOP ---
        while step_count < max_steps:
            # 1. Fetch History
            history = state_manager.get_session_history(session_id)

            # 2. Plan (Dynamic: Based on latest history)
            plan_data = planner.generate_plan(history, user_request)
            preamble = plan_data.get("preamble")
            plan = plan_data.get("plan", [])

            # Display agent thought process (optional, good for debugging/transparency)
            if preamble and step_count == 0:
                print(f"Assistant: {preamble}")
                # We don't save every preamble to history to save context tokens,
                # but you can if you want conversational continuity.
                state_manager.add_message(
                    session_id=session_id, role="assistant", content=preamble)

            if not plan:
                print("Assistant: I couldn't create a plan. Ending turn.")
                state_manager.add_message(
                    session_id=session_id, role="assistant", content="I couldn't create a plan.")
                break

            # 3. Execute ONLY the first step (ReAct pattern)
            # Even if the planner returned 5 steps, we only do the first one
            # to ensure we observe the result before proceeding.
            current_step = plan[0]
            tool_to_use = current_step.get("tool_to_use")
            description = current_step.get("description")

            print(f"\n[Step {step_count + 1}] Thought: {description}")
            state_manager.add_message(
                session_id=session_id, role="assistant", content=description)

            # 4. Safety Check for Write AND Edit
            if tool_to_use in ["write_file", "edit_file"]:
                filepath = current_step.get("parameters", {}).get("filepath")
                print(f"ATTENTION: Modifying file '{filepath}' via {tool_to_use}.")
                confirmation = input("Allow? (y/n): ")
                if confirmation.lower() != 'y':
                    observation = "User denied permission."
                    print(f"Observation: {observation}")
                    state_manager.add_message(session_id=session_id, role="observation", tool_used=tool_to_use, content=observation)
                    step_count += 1
                    continue

            # 5. Execute Tool
            observation = executor.execute_step(current_step)

            # 6. Handle Final Answer
            if tool_to_use == "final_answer":
                print(f"\nAssistant: {observation}\n")
                state_manager.add_message(
                    session_id=session_id, role="assistant", content=observation)
                break  # Exit the Agent Loop, wait for new user input

            # 7. Handle Standard Observation
            else:
                print(f"Observation: {observation}")
                # Save the observation so the Planner sees it in the next iteration
                state_manager.add_message(
                    session_id=session_id,
                    role="observation",
                    tool_used=tool_to_use,
                    content=str(observation)
                )

            step_count += 1

        if step_count >= max_steps:
            print("Error: Maximum steps reached. The agent may be stuck in a loop.")


if __name__ == "__main__":
    main()
