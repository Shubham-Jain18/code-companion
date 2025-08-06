from planner import Planner
from executor import Executor

def main():
    """The main orchestrator loop for the AI Code Companion."""
    
    planner = Planner()
    executor = Executor()
    history = []

    print("="*50)
    print("Welcome to your AI Code Companion!")
    print("Type 'exit' to end the session.")
    print("="*50)

    while True:
        user_request = input("You: ")
        if user_request.lower() == 'exit':
            print("Assistant: Goodbye!")
            break

        history.append({"role": "user", "content": user_request})

        # 1. Planning Phase
        plan_data = planner.generate_plan(history, user_request)
        preamble = plan_data.get("preamble")
        plan = plan_data.get("plan", [])

        if preamble:
            print(f"Assistant: {preamble}")

        if not plan:
            print("Assistant: I couldn't create a plan for that. Please try rephrasing.")
            history.append({"role": "assistant", "content": "I couldn't create a plan for that."})
            continue
        
        # 2. Display Plan and Execute
        print("\n--- EXECUTING PLAN ---")
        for i, step in enumerate(plan):
            print(f"Executing Step {i+1}: {step.get('description')}")
            
            # Add a safety check for the 'write_file' tool
            if step.get("tool_to_use") == "write_file":
                filepath = step.get("parameters", {}).get("filepath")
                print("-" * 20)
                print(f"ATTENTION: The agent wants to write to the file '{filepath}'.")
                print("-" * 20)
                confirmation = input("Do you want to allow this action? (y/n): ")
                if confirmation.lower() != 'y':
                    observation = "Action cancelled by user."
                    print(f"Observation: {observation}\n")
                    history.append({"role": "observation", "tool": "write_file", "content": observation})
                    continue
            
            observation = executor.execute_step(step)
            # For `final_answer`, the observation is the answer itself.
            # For other tools, it's the result of the tool execution.
            if step.get("tool_to_use") == "final_answer":
                 print(f"Assistant: {observation}\n")
            else:
                print(f"Observation: {observation}\n")
            
            history.append({"role": "observation", "tool": step.get('tool_to_use'), "content": observation})
        print("--- PLAN COMPLETE ---\n")

if __name__ == "__main__":
    main()
