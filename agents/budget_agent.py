from crewai import Agent, Task

def create_budget_planner():
    """Agent that helps create a personalized budget."""
    
    agent = Agent(
        role="Budget Planner",
        goal="Create a realistic, personalized monthly budget",
        backstory="""You are an expert budget planner. You help people create 
        realistic budgets that account for their actual spending patterns 
        while leaving room for savings and financial goals.""",
        allow_delegation=False,
        verbose=True
    )
    
    task = Task(
        description="""Create a monthly budget plan based on the expense analysis.
        Include: income needed, expense breakdown by category, emergency fund target, 
        and savings goals.""",
        expected_output="A detailed monthly budget plan with percentages and amounts",
        agent=agent
    )
    
    return agent, task