from planner import Planner
from executor import Executor
from state_manager import StateManager

def main():
    """The main orchestrator loop for the AI Code Companion."""
    
    # Instantiate our core components
    planner = Planner()
    executor = Executor()
    state_manager = StateManager() # Use the new state manager

    # Create a new session for this run
    session_id = state_manager.create_new_session()

    print("="*50)
    print("Welcome to your AI Code Companion!")
    print(f"Session ID: {session_id}")
    print("Type 'exit' to end the session.")
    print("="*50)

    while True:
        user_request = input("You: ")
        if user_request.lower() == 'exit':
            print("Assistant: Goodbye!")
            break

        # Save user message to persistent history
        state_manager.add_message(session_id=session_id, role="user", content=user_request)
        
        # Get the up-to-date history for the planner
        history = state_manager.get_session_history(session_id)

        # 1. Planning Phase
        plan_data = planner.generate_plan(history, user_request)
        preamble = plan_data.get("preamble")
        plan = plan_data.get("plan", [])

        if preamble:
            print(f"Assistant: {preamble}")
            # Save the preamble to history
            state_manager.add_message(session_id=session_id, role="assistant", content=preamble)

        if not plan:
            print("Assistant: I couldn't create a plan for that. Please try rephrasing.")
            state_manager.add_message(session_id=session_id, role="assistant", content="I couldn't create a plan for that.")
            continue
        
        # 2. Display Plan and Execute
        print("\n--- EXECUTING PLAN ---")
        for i, step in enumerate(plan):
            print(f"Executing Step {i+1}: {step.get('description')}")
            
            tool_to_use = step.get("tool_to_use")
            if tool_to_use == "write_file":
                filepath = step.get("parameters", {}).get("filepath")
                print("-" * 20)
                print(f"ATTENTION: The agent wants to write to the file '{filepath}'.")
                print("-" * 20)
                confirmation = input("Do you want to allow this action? (y/n): ")
                if confirmation.lower() != 'y':
                    observation = "Action cancelled by user."
                    print(f"Observation: {observation}\n")
                    state_manager.add_message(session_id=session_id, role="observation", tool_used="write_file", content=observation)
                    continue
            
            observation = executor.execute_step(step)
            
            if tool_to_use == "final_answer":
                 print(f"Assistant: {observation}\n")
                 state_manager.add_message(session_id=session_id, role="assistant", content=observation)
            else:
                print(f"Observation: {observation}\n")
                state_manager.add_message(session_id=session_id, role="observation", tool_used=tool_to_use, content=observation)

        print("--- PLAN COMPLETE ---\n")

if __name__ == "__main__":
    main()