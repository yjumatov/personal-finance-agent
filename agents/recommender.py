from crewai import Agent, Task

def create_recommender():
    agent = Agent(
        role="Personal Finance Advisor",
        goal="Provide actionable financial recommendations based on spending analysis",
        backstory="You are an experienced personal finance advisor who helps people optimize their budgets.",
        allow_delegation=False,
        verbose=True
    )
    
    task = Task(
        description="""Based on the expense analysis, create personalized recommendations:
        1. Top 3 areas to cut spending (with specific suggestions)
        2. Simple money-saving tips (easy wins)
        3. Suggested monthly budget breakdown
        4. One financial goal based on savings potential
        5. Implementation steps""",
        expected_output="A structured recommendation report with specific actions to save money",
        agent=agent
    )
    
    return agent, task