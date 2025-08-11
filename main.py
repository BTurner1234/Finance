import streamlit as st

# ---- Tax and deduction functions ----
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

# Salary as text input (no spinner)
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

# Regular expenses
rent = st.number_input("Monthly rent (£):", min_value=0.0, value=800.0, step=10.0, format="%.2f")
food = st.number_input("Weekly food (£):", min_value=0.0, value=50.0, step=1.0, format="%.2f")

# Other expenses (dynamic)
st.markdown("**Other Expenses (e.g. subscriptions, bills, travel, etc.)**")
expense_count = st.number_input("How many other expense items would you like to enter?", min_value=0, max_value=20, value=0, step=1)

other_expenses = []
for i in range(expense_count):
    cols = st.columns([3, 2, 2])
    with cols[0]:
        desc = st.text_input(f"Description #{i+1}", key=f"desc_{i}")
    with cols[1]:
        amt = st.number_input("Amount (£):", min_value=0.0, value=0.0, key=f"amt_{i}", format="%.2f")
    with cols[2]:
        freq = st.selectbox("Frequency", ["Weekly", "Monthly"], key=f"freq_{i}")
    other_expenses.append((desc, amt, freq))

# Annualize all expenses
annual_rent = rent * 12
annual_food = food * 52
annual_other = 0
expense_summary = []
for desc, amt, freq in other_expenses:
    if freq == "Weekly":
        v = amt * 52
    else:
        v = amt * 12
    annual_other += v
    expense_summary.append((desc, v))

# Tax and loan deductions
tax = income_tax(salary)
loan1 = undergraduate_loan(salary) if has_undergrad_loan else 0
loan2 = postgraduate_loan(salary) if has_postgrad_loan else 0
ni = national_insurance(salary)

# Total costs
total_expenses = annual_rent + annual_food + annual_other

# Final take-home pay calculation
total_deductions = tax + loan1 + loan2 + ni + total_expenses
take_home = salary - (tax + loan1 + loan2 + ni + total_expenses)

if salary:
    st.header(f"Your take-home pay (after tax and expenses): £{take_home:,.2f}")
    st.subheader(f"Your total yearly costs (excluding tax/loans/NI): £{total_expenses:,.2f}")

    with st.expander("Expand to see full breakdown..."):
        st.write("##### Taxes & Deductions")
        st.write(f"Income Tax: £{tax:,.2f}")
        st.write(f"National Insurance: £{ni:,.2f}")
        st.write(f"Undergraduate Loan: £{loan1:,.2f}")
        st.write(f"Postgraduate Loan: £{loan2:,.2f}")
        st.write(" ")
        st.write("##### Living and Other Expenses")
        st.write(f"Rent: £{annual_rent:,.2f}")
        st.write(f"Food: £{annual_food:,.2f}")
        for desc, v in expense_summary:
            st.write(f"{desc or 'Other'}: £{v:,.2f}")

else:
    st.info("Please enter your salary to calculate results.")
