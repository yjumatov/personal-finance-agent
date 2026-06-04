import os
from dotenv import load_dotenv
import requests

load_dotenv()

def analyze_finances(expense_data):
    print("\n=== Starting Analysis ===")
    
    if isinstance(expense_data, list):
        expense_text = "Here are my transactions:\n"
        for exp in expense_data:
            if isinstance(exp, dict):
                expense_text += f"- {exp.get('date', '')}: {exp.get('description', '')} - ${exp.get('amount', 0)}\n"
    else:
        expense_text = str(expense_data)
    
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {"status": "error", "error": "No API key", "analysis": "Error", "recommendations": "Error", "budget": "Error"}
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        print("Step 1: Analysis...")
        
        analysis_prompt = f"""Analyze these expenses. Provide a PLAIN TEXT response (no markdown, no ** bold, no ### headers, no tables):

{expense_text}

Include:
- Categorized expenses breakdown
- Total spending by category with percentages
- Top 3 spending categories
- Unusual spending patterns
- Summary of spending habits

Use clear paragraphs and simple formatting only."""
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={"model": "claude-opus-4-1", "max_tokens": 1000, "messages": [{"role": "user", "content": analysis_prompt}]},
            timeout=60,
            verify=False
        )
        analysis = response.json()["content"][0]["text"] if response.status_code == 200 else "Error"
        print("✓ Analysis done")
        
        print("Step 2: Recommendations...")
        
        rec_prompt = f"""Based on these expenses, provide PLAIN TEXT recommendations (no markdown, no ** bold, no ### headers):

{expense_text}

Include 5-7 specific, actionable recommendations:
- Areas to cut spending with dollar amounts
- Easy wins and quick money-saving tips
- Budget adjustments
- Long-term financial goals
- Action steps to implement

Use clear paragraphs only."""
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={"model": "claude-opus-4-1", "max_tokens": 1000, "messages": [{"role": "user", "content": rec_prompt}]},
            timeout=60,
            verify=False
        )
        recommendations = response.json()["content"][0]["text"] if response.status_code == 200 else "Error"
        print("✓ Recommendations done")
        
        print("Step 3: Budget plan...")
        
        budget_prompt = f"""Create a PLAIN TEXT monthly budget plan (no markdown, no ** bold, no ### headers, no tables):

Based on these expenses:
{expense_text}

Include:
- Recommended spending percentages by category
- Monthly budget amounts for each category
- Emergency fund target
- Savings goals
- Budget limits and priorities

Use clear paragraphs and simple lists only."""
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={"model": "claude-opus-4-1", "max_tokens": 1000, "messages": [{"role": "user", "content": budget_prompt}]},
            timeout=60,
            verify=False
        )
        budget = response.json()["content"][0]["text"] if response.status_code == 200 else "Error"
        print("✓ Budget done")
        
        print("✓ Complete!\n")
        
        return {
            "status": "success",
            "analysis": analysis,
            "recommendations": recommendations,
            "budget": budget,
            "expense_data": expense_data,
            "agents_used": ["Expense Analyzer", "Financial Advisor", "Budget Planner"]
        }
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "analysis": "Error",
            "recommendations": "Error",
            "budget": "Error"
        }