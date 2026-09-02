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
        analyzer_usage = {
            "input_tokens": analysis_response.usage.input_tokens,
            "output_tokens": analysis_response.usage.output_tokens,
        }

        print(f"DEBUG: Got analysis in {elapsed:.2f}s")
        print(f"DEBUG: Analysis length: {len(analysis)} chars")
        print(f"DEBUG: Analyzer tokens — in={analyzer_usage['input_tokens']} out={analyzer_usage['output_tokens']}")
        
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
        recommender_usage = {
            "input_tokens": recommendations_response.usage.input_tokens,
            "output_tokens": recommendations_response.usage.output_tokens,
        }

        print(f"DEBUG: Got recommendations in {elapsed:.2f}s")
        print(f"DEBUG: Recommendations length: {len(recommendations)} chars")
        print(f"DEBUG: Recommender tokens — in={recommender_usage['input_tokens']} out={recommender_usage['output_tokens']}")

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
        budget_planner_usage = {
            "input_tokens": budget_response.usage.input_tokens,
            "output_tokens": budget_response.usage.output_tokens,
        }

        print(f"DEBUG: Got budget plan in {elapsed:.2f}s")
        print(f"DEBUG: Budget planner tokens — in={budget_planner_usage['input_tokens']} out={budget_planner_usage['output_tokens']}")
        print("DEBUG: Analysis complete!\n")

        total_in  = analyzer_usage["input_tokens"] + recommender_usage["input_tokens"] + budget_planner_usage["input_tokens"]
        total_out = analyzer_usage["output_tokens"] + recommender_usage["output_tokens"] + budget_planner_usage["output_tokens"]

        return {
            "status": "success",
            "analysis": analysis,
            "recommendations": recommendations,
            "budget": budget,
            "expense_data": expense_data,
            "agents_used": ["Expense Analyzer", "Personal Finance Advisor", "Budget Planner"],
            "usage": {
                "analyzer":       analyzer_usage,
                "recommender":    recommender_usage,
                "budget_planner": budget_planner_usage,
                "total_input_tokens":  total_in,
                "total_output_tokens": total_out,
            },
        }
    
    except Exception as e:
        print(f"DEBUG: ERROR - {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        return {
            "status": "error",
            "error": str(e),
            "expense_data": expense_data
        }