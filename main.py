from planner import Planner
from executor import Executor

def main():
    """The main orchestrator loop for the AI Code Companion."""
    
    # Instantiate our core components
    planner = Planner()
    executor = Executor()

    # In-memory history for this session. We'll replace this with the StateManager later.
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

        # Add user message to history
        history.append({"role": "user", "content": user_request})

        # 1. Planning Phase
        plan = planner.generate_plan(history, user_request)
        print(f"Assistant's Plan: {plan.get('plan', [])}") # Let's see the plan for debugging

        # 2. Execution Phase
        if not plan or not plan.get('plan'):
            print("Assistant: I'm sorry, I couldn't create a plan for that.")
            history.append({"role": "assistant", "content": "I'm sorry, I couldn't create a plan for that."})
            continue

        for step in plan['plan']:
            observation = executor.execute_step(step)
            print(f"Assistant: {observation}")
            
            # Add the final output to history for the next turn's context
            history.append({"role": "assistant", "content": observation})

if __name__ == "__main__":
    main()
