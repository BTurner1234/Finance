import streamlit as st
import pandas as pd

# ---- Tax and deduction functions (same as before) ----
def income_tax(salary):
    tax = 0
    if salary > 125140:
        tax += (salary - 125140) * 0.45
        salary = 125140
    if salary > 100000:
        tax += (salary - 100000) * 0.50
        salary = 100000
    if salary > 50270:
        tax += (salary - 50270) * 0.40
        salary = 50270
    if salary > 12570:
        tax += (salary - 12570) * 0.20
    return tax

def undergraduate_loan(salary):
    threshold = 28470
    rate = 0.09
    if salary > threshold:
        repayment = (salary - threshold) * rate
    else:
        repayment = 0
    return repayment

def postgraduate_loan(salary):
    threshold = 21000
    rate = 0.06
    if salary > threshold:
        repayment = (salary - threshold) * rate
    else:
        repayment = 0
    return repayment

def national_insurance(salary):
    lower_threshold = 12570
    upper_threshold = 50270
    lower_rate = 0.08
    upper_rate = 0.02

    ni = 0
    if salary > lower_threshold:
        ni += (min(salary, upper_threshold) - lower_threshold) * lower_rate
    if salary > upper_threshold:
        ni += (salary - upper_threshold) * upper_rate

    return ni

# ---- Streamlit app ----
st.title("UK Take-home Pay & Cost Calculator")

salary_str = st.text_input("Enter your gross annual salary (£):", "30000")
try:
    salary = float(salary_str)
except:
    salary = 0.0
    st.warning("Please enter a valid number for salary.")

# Two checkboxes on the same row
col1, col2 = st.columns(2)
with col1:
    has_undergrad_loan = st.checkbox("Undergraduate loan")
with col2:
    has_postgrad_loan = st.checkbox("Postgraduate loan")

# Plain text input for rent and food
rent_str = st.text_input("Monthly rent (£):", "800")
food_str = st.text_input("Weekly food (£):", "50")
try:
    rent = float(rent_str)
except:
    rent = 0.0
try:
    food = float(food_str)
except:
    food = 0.0

# EXPENSES: Use session_state for dynamic expenses table
if "user_expenses" not in st.session_state:
    st.session_state.user_expenses = []

with st.form(key="add_expense_form"):
    cols = st.columns([3, 2, 2])
    with cols[0]:
        exp_desc = st.text_input("Description", key="desc_new")
    with cols[1]:
        exp_amt_str = st.text_input("Amount (£)", "0", key="amt_new")
    with cols[2]:
        exp_freq = st.selectbox("Frequency", ["Weekly", "Monthly"], key="freq_new")
    add = st.form_submit_button("Add Expense")

if add:
    try:
        exp_amt = float(exp_amt_str)
    except:
        exp_amt = 0.0
    st.session_state.user_expenses.append((exp_desc, exp_amt, exp_freq))

# Option to clear all extra expenses
st.markdown("#### Current Extra Expenses")
if st.session_state.user_expenses:
    # Format for display
    display_expenses = []
    for d, a, f in st.session_state.user_expenses:
        display_expenses.append({
            "Description": d, 
            "Amount": f"£{a:,.2f}",
            "Frequency": f
        })
    df = pd.DataFrame(display_expenses)
    st.write(df.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.caption("No extra expenses added.")

# Yearly/monthly toggle
period = st.radio("View breakdown as:", ("Yearly", "Monthly"))

# Annualize all expenses
annual_rent = rent * 12
annual_food = food * 52
annual_other = 0
expense_summary = []
for desc, amt, freq in st.session_state.user_expenses:
    if freq == "Weekly":
        v = amt * 52
    else:
        v = amt * 12
    annual_other += v
    expense_summary.append((desc, v))

# Tax and loan deductions (annual)
tax = income_tax(salary)
loan1 = undergraduate_loan(salary) if has_undergrad_loan else 0
loan2 = postgraduate_loan(salary) if has_postgrad_loan else 0
ni = national_insurance(salary)
total_expenses = annual_rent + annual_food + annual_other
total_deductions = tax + loan1 + loan2 + ni + total_expenses
take_home = salary - total_deductions

# Monthly values
monthly_salary = salary / 12
monthly_tax = tax / 12
monthly_ni = ni / 12
monthly_loan1 = loan1 / 12
monthly_loan2 = loan2 / 12
monthly_expenses = total_expenses / 12
monthly_take_home = take_home / 12

if salary:
    if period == "Yearly":
        st.header(f"Your take-home pay (after tax and expenses): £{take_home:,.2f} per year")
        st.subheader(f"Your total yearly costs (excluding tax/loans/NI): £{total_expenses:,.2f}")
    else:
        st.header(f"Your take-home pay (after tax and expenses): £{monthly_take_home:,.2f} per month")
        st.subheader(f"Your total monthly costs (excluding tax/loans/NI): £{monthly_expenses:,.2f}")

    with st.expander("Expand to see full breakdown..."):
        if period == "Yearly":
            st.write("##### Taxes & Deductions (Yearly)")
            st.write(f"Income Tax: £{tax:,.2f}")
            st.write(f"National Insurance: £{ni:,.2f}")
            st.write(f"Undergraduate Loan: £{loan1:,.2f}")
            st.write(f"Postgraduate Loan: £{loan2:,.2f}")
            st.write(" ")
            st.write("##### Living and Other Expenses (Yearly)")
            st.write(f"Rent: £{annual_rent:,.2f}")
            st.write(f"Food: £{annual_food:,.2f}")
            for desc, v in expense_summary:
                st.write(f"{desc or 'Other'}: £{v:,.2f}")
        else:
            st.write("##### Taxes & Deductions (Monthly)")
            st.write(f"Income Tax: £{monthly_tax:,.2f}")
            st.write(f"National Insurance: £{monthly_ni:,.2f}")
            st.write(f"Undergraduate Loan: £{monthly_loan1:,.2f}")
            st.write(f"Postgraduate Loan: £{monthly_loan2:,.2f}")
            st.write(" ")
            st.write("##### Living and Other Expenses (Monthly)")
            st.write(f"Rent: £{rent:,.2f}")
            st.write(f"Food: £{food:,.2f}")
            for idx, (desc, v) in enumerate(expense_summary):
                freq = st.session_state.user_expenses[idx][2]
                if freq == "Weekly":
                    monthly_v = v / 12
                else:
                    monthly_v = v / 12
                st.write(f"{desc or 'Other'}: £{monthly_v:,.2f}")
else:
    st.info("Please enter your salary to calculate results.")