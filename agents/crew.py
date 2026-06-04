from crewai import Crew, Process
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import time

load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def analyze_finances(expense_data):
    """Analyze finances using Claude with debug output"""
    
    print("\n=== DEBUG: Starting Analysis ===")
    
    # Format expenses
    if isinstance(expense_data, list):
        expense_text = "Here are my transactions:\n"
        for exp in expense_data:
            if isinstance(exp, dict):
                expense_text += f"- {exp.get('date', '')}: {exp.get('description', '')} - ${exp.get('amount', 0)}\n"
            else:
                expense_text += f"- {exp}\n"
    else:
        expense_text = str(expense_data)
    
    print(f"DEBUG: Expenses formatted: {len(expense_text)} chars")
    
    try:
        # Get expense analysis
        print("DEBUG: Calling Claude for expense analysis...")
        
        analysis_prompt = f"""Analyze these expenses:

{expense_text}

Provide:
1. Categorized list
2. Totals by category
3. Top 3 categories
4. Any unusual spending"""
        
        start_time = time.time()
        
        analysis_response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": analysis_prompt}
            ]
        )
        
        elapsed = time.time() - start_time
        analysis = analysis_response.content[0].text
        
        print(f"DEBUG: Got analysis in {elapsed:.2f}s")
        print(f"DEBUG: Analysis length: {len(analysis)} chars")
        
        # Get recommendations
        print("DEBUG: Calling Claude for recommendations...")
        
        recommendation_prompt = f"""Based on this analysis:

{analysis}

Provide 3 ways to save money."""
        
        start_time = time.time()
        
        recommendations_response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": recommendation_prompt}
            ]
        )
        
        elapsed = time.time() - start_time
        recommendations = recommendations_response.content[0].text
        
        print(f"DEBUG: Got recommendations in {elapsed:.2f}s")
        print(f"DEBUG: Recommendations length: {len(recommendations)} chars")

        # Get budget plan
        print("DEBUG: Calling Claude for budget plan...")

        budget_prompt = f"""Based on these expenses and analysis:

{analysis}

Create a recommended monthly budget with:
1. Budget breakdown by category (percentages)
2. Monthly income needed
3. Emergency fund target
4. Savings goal amount"""

        start_time = time.time()

        budget_response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": budget_prompt}
            ]
        )

        elapsed = time.time() - start_time
        budget = budget_response.content[0].text

        print(f"DEBUG: Got budget plan in {elapsed:.2f}s")
        print("DEBUG: Analysis complete!\n")

        return {
            "status": "success",
            "analysis": analysis,
            "recommendations": recommendations,
            "budget": budget,
            "expense_data": expense_data,
            "agents_used": ["Expense Analyzer", "Personal Finance Advisor", "Budget Planner"]
        }
    
    except Exception as e:
        print(f"DEBUG: ERROR - {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        return {
            "status": "error",
            "error": str(e),
            "expense_data": expense_data
        }