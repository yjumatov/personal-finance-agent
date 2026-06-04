from crewai import Agent, Task

def create_expense_analyzer():
    agent = Agent(
        role="Expense Analyzer",
        goal="Categorize user expenses and identify spending patterns",
        backstory="You are a financial analyst specializing in personal expense analysis.",
        allow_delegation=False,
        verbose=True
    )
    
    task = Task(
        description="""Analyze the provided expense data and:
        1. Categorize each expense by type
        2. Calculate total spending by category
        3. Identify the top 3 spending categories
        4. Flag any unusual or high transactions
        5. Provide a summary of spending patterns""",
        expected_output="A detailed expense analysis including categorized expenses, spending totals, and patterns",
        agent=agent
    )
    
    return agent, task