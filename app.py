
from pathlib import Path
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_advisor import generate_saving_strategies


# -------------------------------
# 1. Page configuration
# -------------------------------

st.set_page_config(
    page_title="Smart Expense Manager",
    page_icon="💰",
    layout="wide",
)

st.title("Smart Expense Manager")
st.caption("Track your spending. Understand your habits. Save smarter.")


# -------------------------------
# 2. Application settings
# -------------------------------

CATEGORIES = [
    "Food",
    "Fare",
    "Stationary",
    "Health",
    "Entertainment",
    "Others",
]

DATA_FILE = Path(__file__).parent / "expenses.csv"

COLUMNS = ["Date", "Category", "Amount", "Description"]


# -------------------------------
# 3. CSV storage functions
# -------------------------------

def load_expenses():
    """Load saved expenses or create an empty CSV file."""

    if not DATA_FILE.exists():
        empty_df = pd.DataFrame(columns=COLUMNS)
        empty_df.to_csv(DATA_FILE, index=False)
        return empty_df

    try:
        df = pd.read_csv(DATA_FILE)

        # Handle an empty CSV file.
        if df.empty and len(df.columns) == 0:
            return pd.DataFrame(columns=COLUMNS)

        # Ensure all required columns exist.
        for column in COLUMNS:
            if column not in df.columns:
                df[column] = None

        df = df[COLUMNS].copy()
        df["Date"] = pd.to_datetime(
            df["Date"], errors="coerce"
        ).dt.date
        df["Amount"] = pd.to_numeric(
            df["Amount"], errors="coerce"
        )

        df = df.dropna(subset=["Date", "Category", "Amount"])
        df = df[df["Category"].isin(CATEGORIES)]
        df = df[df["Amount"] > 0]

        return df

    except (OSError, ValueError, pd.errors.ParserError):
        st.error(
            "Could not read expenses.csv. "
            "Check that the file is valid and accessible."
        )
        return pd.DataFrame(columns=COLUMNS)


def save_expense(category, amount, expense_date, description):
    """Append one expense to the CSV file."""

    new_expense = pd.DataFrame(
        [{
            "Date": expense_date,
            "Category": category,
            "Amount": amount,
            "Description": description,
        }]
    )

    file_exists = DATA_FILE.exists()

    new_expense.to_csv(
        DATA_FILE,
        mode="a",
        header=not file_exists,
        index=False,
    )


# -------------------------------
# 4. Expense entry form
# -------------------------------

st.subheader("Add a new expense")

with st.form("expense_form", clear_on_submit=True):
    category = st.selectbox(
        "Select category",
        CATEGORIES,
    )

    amount = st.number_input(
        "Amount (PKR)",
        min_value=0.0,
        value=None,
        step=10.0,
        format="%.2f",
        placeholder="Enter amount, e.g. 120",
    )

    expense_date = st.date_input(
        "Expense date",
        value=date.today(),
    )

    description = st.text_input(
        "Description (optional)",
        placeholder="e.g. Lunch, bus fare, notebook",
        max_chars=150,
    )

    submitted = st.form_submit_button(
        "Add Expense",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if amount is None or amount <= 0:
            st.error("Please enter an amount greater than zero.")
        else:
            try:
                save_expense(
                    category,
                    amount,
                    expense_date,
                    description.strip(),
                )
                st.success("Expense saved successfully.")
                st.rerun()

            except OSError:
                st.error(
                    "Unable to save the expense. "
                    "Check write permissions for the project folder."
                )


# -------------------------------
# 5. Load data and set budget
# -------------------------------

expenses = load_expenses()

st.divider()
st.subheader("Your spending dashboard")

monthly_budget = st.number_input(
    "Monthly budget (PKR)",
    min_value=0.0,
    value=10000.0,
    step=500.0,
    format="%.2f",
    key="monthly_budget",
)

# Analyze the current month.
current_month = date.today().strftime("%Y-%m")

if not expenses.empty:
    expenses["Month"] = pd.to_datetime(
        expenses["Date"]
    ).dt.strftime("%Y-%m")

    monthly_expenses = expenses[
        expenses["Month"] == current_month
    ].copy()
else:
    monthly_expenses = pd.DataFrame(columns=COLUMNS)


# -------------------------------
# 6. Summary metrics
# -------------------------------

total_spent = float(monthly_expenses["Amount"].sum())
remaining = monthly_budget - total_spent

col1, col2, col3 = st.columns(3)

col1.metric(
    "Spent this month",
    f"Rs. {total_spent:,.2f}",
)

col2.metric(
    "Monthly budget",
    f"Rs. {monthly_budget:,.2f}",
)

col3.metric(
    "Budget remaining",
    f"Rs. {remaining:,.2f}",
    delta=f"{remaining:,.2f} PKR",
    delta_color="normal" if remaining >= 0 else "inverse",
)

if monthly_budget > 0:
    progress = min(total_spent / monthly_budget, 1.0)

    st.progress(progress)

    if total_spent > monthly_budget:
        st.warning("You have exceeded your monthly budget.")
    elif total_spent >= monthly_budget * 0.8:
        st.warning("You have used at least 80% of your monthly budget.")
    else:
        st.caption(
            f"You have used {progress:.1%} of your monthly budget."
        )


# -------------------------------
# 7. Category-wise analytics
# -------------------------------

st.subheader("Category-wise spending")

if not monthly_expenses.empty:
    category_totals = (
        monthly_expenses
        .groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_pie = px.pie(
            category_totals,
            names="Category",
            values="Amount",
            hole=0.45,
            title="Spending distribution",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        fig_bar = px.bar(
            category_totals,
            x="Category",
            y="Amount",
            title="Spending by category",
            labels={
                "Category": "Category",
                "Amount": "Amount (PKR)",
            },
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(
        category_totals,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "No expenses recorded for this month yet. "
        "Add your first expense to see your analytics."
    )


# -------------------------------
# 8. Expense history
# -------------------------------

st.subheader("Expense history")

if not expenses.empty:
    history = expenses.sort_values(
        "Date", ascending=False
    ).drop(columns=["Month"], errors="ignore")

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )

if st.button("Clear Expense History", type="secondary"):
    st.session_state.expenses = []

    # Clear previously generated AI recommendations
if "strategy" in st.session_state:
    del st.session_state["strategy"]

st.rerun()

csv_data = expenses[COLUMNS].to_csv(index=False).encode("utf-8")

st.download_button(
        "Download all expenses as CSV",
        data=csv_data,
        file_name="my_expenses.csv",
        mime="text/csv",
    )
else:
    st.write("Your expense history will appear here.")


# -------------------------------
# 9. AI saving strategies
# -------------------------------

st.divider()
st.subheader("AI Expense Advisor")

st.write(
    "Get practical suggestions based on your current month's "
    "expense totals and budget."
)

if st.button("Generate Saving Strategies", type="primary"):
    if monthly_expenses.empty:
        st.info("Add at least one expense before requesting AI advice.")
    elif monthly_budget <= 0:
        st.warning("Set a monthly budget greater than zero first.")
    else:
        category_summary = (
            monthly_expenses
            .groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
            .to_string()
        )

        with st.spinner("Analyzing your spending..."):
            advice = generate_saving_strategies(
                expense_summary=category_summary,
                total=total_spent,
                budget=monthly_budget,
            )

        st.markdown("### Your saving plan")
        st.markdown(advice)


st.caption(
    "Smart Expense Manager | AI suggestions are informational "
    "and are based on the expense data you provide."
)
