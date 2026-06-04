import streamlit as st
import pandas as pd
from agents.crew import analyze_finances
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Streamlit
st.set_page_config(
    page_title="Personal Finance Agent",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Multi-Agent Analyzer")
st.markdown("Analyze your expenses and get personalized financial recommendations")

# Add this after st.set_page_config
if 'expenses_list' not in st.session_state:
    st.session_state.expenses_list = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Sidebar for input
st.sidebar.header("📊 Input Your Expenses")

# Option 1: Manual Entry
input_method = st.sidebar.radio(
    "How would you like to input expenses?",
    ["Manual Entry", "Upload CSV", "Paste Text"]
)

expenses = []

if input_method == "Manual Entry":
    st.sidebar.subheader("Add Expenses One by One")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.now())
    with col2:
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
    
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Healthcare", "Other"]
    )
    
    description = st.text_input("Description (optional)")
    
    # Use regular button instead of form
    if st.sidebar.button("Add Expense"):
        if amount > 0:
            new_expense = {
                "date": str(date),
                "description": f"{category}: {description}" if description else category,
                "amount": amount,
                "category": category
            }
            
            # Store in session state
            if 'expenses_list' not in st.session_state:
                st.session_state.expenses_list = []
            
            st.session_state.expenses_list.append(new_expense)
            st.sidebar.success("✅ Expense added!")
        else:
            st.sidebar.error("Please enter an amount greater than 0")
    
    # Show added expenses
    if 'expenses_list' in st.session_state and st.session_state.expenses_list:
        st.sidebar.write("### Your Expenses")
        for i, exp in enumerate(st.session_state.expenses_list):
            st.sidebar.write(f"{i+1}. {exp['date']} - {exp['description']} - ${exp['amount']}")
        
        # Use the stored list
        expenses = st.session_state.expenses_list

elif input_method == "Upload CSV":
    st.sidebar.subheader("Upload CSV File")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.write("✅ File loaded successfully")
            st.sidebar.write(df)
            
            # Convert to expense format
            for _, row in df.iterrows():
                expenses.append({
                    "date": str(row.get('date', row.get('Date', ''))),
                    "description": str(row.get('description', row.get('Description', ''))),
                    "amount": float(row.get('amount', row.get('Amount', 0)))
                })
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

else:  # Paste Text
    st.sidebar.subheader("Paste Your Expense Data")
    text_input = st.sidebar.text_area(
        "Paste expenses (one per line, format: DATE DESCRIPTION AMOUNT)",
        height=150,
        placeholder="2024-01-15 Grocery Shopping 50.25\n2024-01-16 Gas 45.00"
    )
    
    if text_input:
        expenses_text = text_input

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Analysis")
    
    if expenses or input_method == "Paste Text":
        if st.button("🔍 Analyze My Finances", key="analyze_button"):
            if not expenses and input_method == "Paste Text":
                # Use text input directly
                expense_input = text_input
            else:
                expense_input = expenses
            
            if not expense_input:
                st.error("❌ Please enter at least one expense")
            else:
                with st.spinner("🤔 Analyzing your finances with AI agents..."):
                    try:
                        st.write("**DEBUG: Starting analysis...**")  # Add debug line
                        result = analyze_finances(expense_input)
                        st.write("**DEBUG: Analysis returned**")  # Add debug line
        
                        if result.get('status') == 'error':
                            st.error(f"❌ Analysis Error: {result.get('error')}")
                        else:
                            st.session_state.analysis_result = result
                            st.success("✅ Analysis complete!")
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
                        st.write(f"**DEBUG: Exception: {str(e)}**")
                        st.info("Make sure your ANTHROPIC_API_KEY is set in .env file")
    else:
        st.info("👈 Enter your expenses first in the sidebar")

with col2:
    st.subheader("📝 Quick Stats")
    if expenses:
        total = sum(e['amount'] for e in expenses)
        st.metric("Total Spent", f"${total:.2f}")
        st.metric("Number of Transactions", len(expenses))
        
        # Category breakdown
        if all('category' in e for e in expenses):
            categories = {}
            for e in expenses:
                cat = e.get('category', 'Other')
                categories[cat] = categories.get(cat, 0) + e['amount']
            
            st.write("**Top Categories:**")
            for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]:
                st.write(f"- {cat}: ${amt:.2f}")

# Display results
if st.session_state.analysis_result:
    st.divider()
    st.subheader("📊 Financial Analysis & Recommendations")

    result_text = st.session_state.analysis_result.get('analysis', '')
    st.write(result_text)

    # Show recommendations
    st.subheader("💡 Money-Saving Recommendations")
    recommendations_text = st.session_state.analysis_result.get('recommendations', '')
    st.write(recommendations_text)

    # Show budget plan
    if 'budget' in st.session_state.analysis_result:
        st.subheader("📈 Recommended Monthly Budget")
        budget_text = st.session_state.analysis_result.get('budget', '')
        st.write(budget_text)

    # Export button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Report"):
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "expenses": st.session_state.analysis_result.get('expense_data'),
                "analysis": st.session_state.analysis_result.get('analysis'),
                "recommendations": st.session_state.analysis_result.get('recommendations'),
                "budget": st.session_state.analysis_result.get('budget', 'N/A')
            }

            report_json = json.dumps(report_data, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# Footer
st.divider()
st.markdown("""
---
**About This Tool**: This is a personal finance agent that uses AI to analyze your expenses 
and provide personalized recommendations. Your data is processed locally and not stored on any server.

**How it works**:
1. Enter your expenses (manually, CSV, or text)
2. Click "Analyze My Finances"
3. AI agents analyze your spending and provide recommendations
4. Download your report for future reference

**Note**: This tool is for educational purposes and personal finance learning.
""")