import marimo

__generated_with = "0.11.25"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import numpy as np
    import altair as alt
    import pandas as pd
    import marimo as mo
    return alt, mo, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # House Affordability Calculator

        ## 28/36 Rule
        No more than **28%** of the borrower’s gross monthly income should be spent on housing costs. Housing costs typically includes:

        - Mortgage principal and interest

        - Property taxes

        - Homeowners insurance

        No more than **36%** spent on total debt costs. This includes housing plus other debts like:

        - Car loans

        - Credit card payments

        - Student loans
        """
    )
    return


@app.cell
def _(mo):
    income_input = mo.ui.number(label="Annual Income (Gross):", value=100_000)

    # Housing Costs
    house_price_input = mo.ui.number(label="House Price:", value=450_000)
    down_payment_input = mo.ui.number(label="Down Payment:", value=50_000)
    interest_rate_input = mo.ui.number(label="Interest Rate (%):", value=6.80)
    property_taxes_input = mo.ui.number(label="Property Taxes (annual):", value=0)
    # property_taxes_input = mo.ui.number(label="Property Taxes (annual):", value=house_price_input.value * 0.0202)
    pmi_input = mo.ui.number(label="Private Mortgage Insurance (PMI annual):", value=0)
    loan_term = mo.ui.dropdown(label='Loan Term (years):', value=30, options=[30, 15])

    # Non-Housing Related Monthly Expenses
    student_loans_input = mo.ui.number(label="Student Loans:", value=1000)
    car_payments_input = mo.ui.number(label="Car Payments:", value=400)
    food_input = mo.ui.number(label="Groceries/Food:", value=400)
    other_expenses_input = mo.ui.number(label="Other Expenses:", value=500)

    # Parameters
    pmi_rate = 0.0055
    property_tax_rate = 0.0202
    utilities = 465

    # Group housing settings
    housing_settings = mo.vstack(
        [
            mo.md("**Housing Costs**"),
            house_price_input,
            interest_rate_input,
            down_payment_input,
            # property_taxes_input,
            loan_term
        ]
    )

    # Group other expenses
    other_expenses = mo.vstack(
        [
            mo.md("**Non-Housing Related Monthly Expenses**"),
            student_loans_input,
            car_payments_input,
            food_input,
            other_expenses_input
        ]
    )

    # Display UI
    mo.vstack(
        [
            mo.md("## User Inputs"),
            income_input,
            mo.hstack([housing_settings, other_expenses], gap=10),
            # mo.md("## FAQ"),
            mo.accordion({
                "Closing Costs": (
                    """
                    Closing costs typically range from 2% to 5% of the home’s purchase price. 
                    Fees can vary between lenders, so shop around for the lowest rates on things like home insurance and title insurance
                    (source: https://www.nerdwallet.com/article/mortgages/closing-costs-mortgage-fees-explained).
                    """
                ), 
                "Private Mortgage Insurance (PMI)": (
                    f"""
                    PMI is added as a monthly expense when the down payment is less than 20%. 
                    It is found using a rate of {pmi_rate:.2%}.
                    """
                ),
                "Property Taxes": (
                    f"""
                    Property taxes can vary widely depending on the location of the property. 
                    The median Dane County effective property tax rate is {property_tax_rate:.2%}.
                    """
                ),
                "Utilities": (
                    f"""
                    I'm making some assumptions based on 2025 data and estimating ${utilities} monthly.
                
                    - [Madison Gas & Electric Estimates by Address](https://www.mge.com/my-account/energy-service/estimate-energy-costs)
                    """
                ),
            })
        ],
        gap=1

    )
    return (
        car_payments_input,
        down_payment_input,
        food_input,
        house_price_input,
        housing_settings,
        income_input,
        interest_rate_input,
        loan_term,
        other_expenses,
        other_expenses_input,
        pmi_input,
        pmi_rate,
        property_tax_rate,
        property_taxes_input,
        student_loans_input,
        utilities,
    )


@app.cell
def _(
    car_payments_input,
    down_payment_input,
    food_input,
    house_price_input,
    income_input,
    interest_rate_input,
    loan_term,
    other_expenses_input,
    pmi_rate,
    property_tax_rate,
    property_taxes_input,
    student_loans_input,
):
    def calculate_mortgage_payment(loan_amount, loan_term_years, annual_interest_rate):
        monthly_interest_rate = annual_interest_rate / 100 / 12
        total_payments = loan_term_years * 12

        if monthly_interest_rate > 0:
            monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**total_payments / \
                              ((1 + monthly_interest_rate)**total_payments - 1)
        else:
            monthly_payment = loan_amount / total_payments

        return monthly_payment


    def calculate_monthly_housing_cost(loan_amount, annual_interest_rate, loan_term_years, property_tax_rate, pmi_rate):
        monthly_mortgage = calculate_mortgage_payment(
            loan_amount,
            loan_term_years,
            annual_interest_rate
        )
    
        pmi_monthly = pmi_rate * loan_amount / 12

        # Should be home price instead of loan amount, but this is easier.
        property_tax_monthly = loan_amount * property_tax_rate / 12

        monthly_housing_cost = monthly_mortgage + property_tax_monthly + pmi_monthly
        return monthly_housing_cost
    

    loan_amount = house_price_input.value - down_payment_input.value

    pmi_annual = pmi_rate * loan_amount
    pmi_monthly = pmi_annual / 12

    property_tax_annual = property_taxes_input.value if property_taxes_input.value != 0 else house_price_input.value * property_tax_rate
    property_tax_monthly = property_tax_annual / 12

    # Calculate monthly costs
    monthly_mortgage = calculate_mortgage_payment(
        loan_amount,
        loan_term.value,
        interest_rate_input.value
    )

    # Total monthly housing cost
    housing_cost_monthly = monthly_mortgage + property_tax_monthly + pmi_monthly
    housing_cost_annual = housing_cost_monthly * 12

    # Total monthly non-housing costs
    non_housing_cost_monthly = student_loans_input.value + car_payments_input.value + food_input.value + other_expenses_input.value
    non_housing_cost_annual = non_housing_cost_monthly * 12

    # Total monthly expenses
    monthly_expenses = housing_cost_monthly + non_housing_cost_monthly

    # Percentages of income
    percent_income_housing = (housing_cost_annual / income_input.value) * 100
    percent_income_non_housing = (non_housing_cost_annual / income_input.value) * 100
    percent_income_total = percent_income_housing + percent_income_non_housing
    return (
        calculate_monthly_housing_cost,
        calculate_mortgage_payment,
        housing_cost_annual,
        housing_cost_monthly,
        loan_amount,
        monthly_expenses,
        monthly_mortgage,
        non_housing_cost_annual,
        non_housing_cost_monthly,
        percent_income_housing,
        percent_income_non_housing,
        percent_income_total,
        pmi_annual,
        pmi_monthly,
        property_tax_annual,
        property_tax_monthly,
    )


@app.cell(hide_code=True)
def _(
    generate_amortization_schedule,
    housing_cost_monthly,
    loan_amount,
    mo,
    monthly_expenses,
    monthly_mortgage,
    percent_income_housing,
    percent_income_non_housing,
    percent_income_total,
    pmi_monthly,
    property_tax_monthly,
):
    text_28 = "**more**" if percent_income_housing > 28 else "less"
    text_36 = "**more**" if percent_income_housing > 28 else "less"
    callout = "warn" if percent_income_total > 36 or percent_income_housing > 28 else "success"

    mo.hstack([
        mo.vstack([
            mo.md(
                """
                ## Results
            
                ### 28/36 Rule
                """
            ),
    
            mo.hstack([
                mo.md("Housing as % of income:"),
                mo.md(f"**{percent_income_housing:.2f}%**")
            ], gap=1, justify='space-between', widths='equal'),
        
            mo.hstack([
                mo.md("Other expenses as % of income:"),
                mo.md(f"**{percent_income_non_housing:.2f}%**")
            ], gap=1, justify='space-between', widths='equal'),
        
            mo.md(""),
            mo.md("---"),
            mo.md(""),
    
            mo.hstack([
                mo.md("Total costs as % of income:"),
                mo.md(f"**{percent_income_total:.2f}%**")
            ], gap=1, justify='space-between', widths='equal'),

            mo.md(
                """
                <br>
                ### Monthly Housing Costs
                """
            ),
            mo.hstack([
                mo.md("Mortgage:"),
                mo.md(f"**${monthly_mortgage:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
    
            mo.hstack([
                mo.md("Property Taxes:"),
                mo.md(f"**${property_tax_monthly:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
    
            mo.hstack([
                mo.md("PMI:"),
                mo.md(f"**${pmi_monthly:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
    
            mo.md(""),
            mo.md("---"),
            mo.md(""),
    
            mo.hstack([
                mo.md("Total:"),
                mo.md(f"**${housing_cost_monthly:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
    
        
        
            mo.md(
                """
                <br>
                ### Other Considerations
                """
            ),
        
            mo.hstack([
                mo.md("Emergency Fund (6 months of expenses):"),
                mo.md(f"**${monthly_expenses*6:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
        
            mo.hstack([
                mo.md("Closing costs:"),
                mo.md(f"**${loan_amount * 0.02:,.0f} - ${loan_amount * 0.05:,.0f}**")
            ], gap=1, justify='space-between', widths='equal'),
            mo.md("<br>")
        ]), 

        mo.vstack([
            mo.md(
                f"""
                Monthly housing costs {text_28} than 28% of gross monthly income.
            
                Total monthly expenses are {text_36} than 36% of gross monthly income.
                """
            ).callout(callout),
            mo.md("### Amortization Schedule"),
            generate_amortization_schedule()])
    
    ], widths='equal')
    return callout, text_28, text_36


@app.cell
def _(
    alt,
    interest_rate_input,
    loan_amount,
    loan_term,
    mo,
    monthly_mortgage,
    pd,
):
    def generate_amortization_schedule():
        # Generate amortization schedule
        amortization_schedule = []
        remaining_balance = loan_amount
        monthly_interest_rate = interest_rate_input.value / 100 / 12
    
        for month in range(1, loan_term.value * 12 + 1):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_mortgage - interest_payment
            remaining_balance -= principal_payment
            amortization_schedule.append({
                'Month': month,
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Remaining Balance': max(remaining_balance, 0)
            })
    
        schedule_df = pd.DataFrame(amortization_schedule)
    
        # Plotting principal vs. interest over time
        chart_data = schedule_df.melt('Month', ['Principal', 'Interest'], var_name='Payment Type', value_name='Amount')
        chart_data['Amount'] = chart_data['Amount'].round(2)
    
        lifetime_mortgage_chart = (
            mo.ui.altair_chart(
                alt.Chart(chart_data).mark_line(strokeWidth=10).encode(
                    x='Month',
                    y='Amount',
                    color='Payment Type'
                ).properties(
                    width=300,
                    height=200,
                ).configure_legend(
                    titleFontSize=14,  # Legend title font size
                    labelFontSize=12,  # Legend label font size
                    symbolSize=1000    # Legend symbol size
                )
            )
        )
        return lifetime_mortgage_chart
    return (generate_amortization_schedule,)


@app.cell
def _():
    ## What-if Analysis
    return


@app.cell(hide_code=True)
def _():
    # def plot_interest_rate_vs_payment(
    #     loan_amount: float,
    #     loan_term_years: int,
    #     base_interest_rate: float,
    #     property_tax_monthly: float,
    #     pmi_monthly: float,
    #     delta_interest_rate: float
    # ):
    #     """
    #     Generates an Altair scatterplot showing how adjustments in interest rates 
    #     affect the monthly payment, over a range of (base_interest_rate ± delta_interest_rate) 
    #     in 0.1% increments. The resulting chart is wrapped in a mo.ui.altair_chart.

    #     Parameters:
    #       - loan_amount: The total loan amount.
    #       - loan_term_years: The term of the loan in years.
    #       - base_interest_rate: The base annual interest rate (in percentage).
    #       - property_tax_monthly: The monthly property tax.
    #       - pmi_monthly: The monthly PMI.
    #       - delta_interest_rate: The deviation (in percentage points) from the base rate.
      
    #     Returns:
    #       A mo.ui.altair_chart object representing the scatterplot.
    #     """
    #     lower_rate = base_interest_rate - delta_interest_rate
    #     higher_rate = base_interest_rate + delta_interest_rate

    #     data = []
    #     current_rate = lower_rate
    #     # Loop in increments of 0.1% until we surpass the higher_rate
    #     while current_rate <= higher_rate + 1e-8:  # epsilon to ensure inclusion
    #         payment = calculate_monthly_housing_cost(
    #             loan_amount,
    #             current_rate,
    #             loan_term_years,
    #             property_tax_monthly,
    #             pmi_monthly
    #         )
    #         data.append({
    #             'Interest Rate (%)': current_rate,
    #             'Monthly Payment': payment
    #         })
    #         # Increment by 0.1% and round to avoid floating point issues
    #         current_rate = round(current_rate + 0.1, 10)

    #     df = pd.DataFrame(data)
    #     df['Monthly Payment'] = df['Monthly Payment'].round(0)
    #     min_payment = df['Monthly Payment'].min()
    #     max_payment = df['Monthly Payment'].max()

    #     chart = alt.Chart(df).mark_circle(size=150).encode(
    #         x=alt.X('Interest Rate (%)', 
    #                 title='Interest Rate (%)',
    #                 scale=alt.Scale(domain=[lower_rate - 0.1, higher_rate + 0.1]),
    #                 axis=alt.Axis(labelExpr="datum.value + '%'")),
    #         y=alt.Y('Monthly Payment', 
    #                 title='Monthly Payment ($)',
    #                 scale=alt.Scale(domain=[min_payment - 100, max_payment + 100]),
    #                 axis=alt.Axis(format="$,d")),
    #        color=alt.condition(
    #             alt.datum["Interest Rate (%)"] == base_interest_rate,
    #             alt.value("orange"),    # Center point is colored orange.
    #             alt.value("steelblue")  # Other points are colored steelblue.
    #         )
    #     ).properties(
    #         width=300,
    #         height=200
    #     ).configure_title(
    #         fontSize=20,
    #     ).configure_axis(
    #         labelFontSize=12,
    #         titleFontSize=14
    #     )

    #     return mo.ui.altair_chart(
    #         chart,
    #         chart_selection="point",
    #         legend_selection=True,
    #         # label="Interest Rate vs. Monthly Payment"
    #     )

    # interest_rate_chart = plot_interest_rate_vs_payment(
    #     loan_amount, 
    #     loan_term.value, 
    #     interest_rate_input.value, 
    #     property_tax_monthly, 
    #     pmi_monthly, 
    #     delta_interest_rate=1.0
    # )

    # interest_rate_chart
    return


@app.cell(hide_code=True)
def _():
    # def plot_house_price_vs_payment(
    #     house_price_input: float,
    #     loan_term_years: int,
    #     interest_rate: float,
    #     property_tax_monthly: float,
    #     pmi_monthly: float,
    #     num_increments: int = 10,
    #     delta_house_price: int = 10000

    # ):
    #     """
    #     Generates an Altair scatterplot showing how increments in house price
    #     affect the monthly payment. It uses house_price_input as the base and 
    #     increases the house price in $10,000 increments.

    #     # Parameters:
    #       - house_price_input: The base starting house price.
    #       - loan_term_years: The term of the loan in years.
    #       - interest_rate: The annual interest rate (in percentage).
    #       - property_tax_monthly: The monthly property tax.
    #       - pmi_monthly: The monthly PMI.
    #       - num_increments: The number of $10k increments to generate data for.
      
    #     Returns:
    #       A mo.ui.altair_chart object representing the scatterplot.
    #     """
    #     price_diff = num_increments * delta_house_price / 2
    #     current_house_price = house_price_input - price_diff
    #     data = []
    #     for i in range(num_increments + 1):
    #         payment = calculate_monthly_housing_cost(
    #             current_house_price,
    #             interest_rate,
    #             loan_term_years,
    #             property_tax_monthly,
    #             pmi_monthly
    #         )
    #         data.append({
    #             'House Price ($)': current_house_price,
    #             'Monthly Payment': payment
    #         })
    #         current_house_price += delta_house_price
    
    #     df = pd.DataFrame(data)
    #     df['Monthly Payment'] = df['Monthly Payment'].round(0)
    #     min_payment = df['Monthly Payment'].min()
    #     max_payment = df['Monthly Payment'].max()

    #     chart = alt.Chart(df).mark_circle(size=150).encode(
    #         x=alt.X('House Price ($)',
    #                 title='House Price ($)',
    #                 scale=alt.Scale(domain=[house_price_input - 1.2*price_diff, house_price_input + 1.2*price_diff]),
    #                 axis=alt.Axis(format="$,d")),
    #         y=alt.Y('Monthly Payment',
    #                 title='Monthly Payment ($)',
    #                 scale=alt.Scale(domain=[min_payment - 100, max_payment + 100]),
    #                 axis=alt.Axis(format="$,d")),
    #         color=alt.condition(
    #             alt.datum["House Price ($)"] == house_price_input,
    #             alt.value("orange"),    # Base house price is highlighted in orange.
    #             alt.value("steelblue")  # Other points are colored steelblue.
    #         )
    #     ).properties(
    #         title='Impact of House Price on Monthly Payment',
    #         width=600,
    #         height=400
    #     ).configure_title(
    #         fontSize=20,
    #     ).configure_axis(
    #         labelFontSize=14,
    #         titleFontSize=16
    #     )

    #     return mo.ui.altair_chart(
    #         chart,
    #         chart_selection="point",
    #         legend_selection=True,
    #         label="House Price vs. Monthly Payment"
    #     )

    # house_price_chart = plot_house_price_vs_payment(
    #     house_price_input.value, 
    #     loan_term.value, 
    #     interest_rate_input.value, 
    #     property_tax_monthly, 
    #     pmi_monthly, 
    #     num_increments=20
    # )

    # house_price_chart
    return


@app.cell
def _(
    alt,
    calculate_monthly_housing_cost,
    house_price_input,
    interest_rate_input,
    loan_term,
    mo,
    pd,
    pmi_rate,
    property_tax_rate,
):
    def plot_interest_rate_and_house_price_vs_payment(
        base_loan_term_years: int,
        base_interest_rate: float,
        delta_interest_rate: float,
        base_house_price: float,
        delta_house_price: int,
        num_price_increments: int,
        property_tax_rate: float,
        pmi_rate: float
    ):
        """
        Plots a single heatmap combining variations in interest rate and house price 
        to illustrate their combined impact on monthly mortgage payment.

        Parameters:
        -----------
          - base_loan_term_years : int
              The term of the loan in years.
          - base_interest_rate : float
              The base annual interest rate (e.g., 6.0 for 6.0%).
          - delta_interest_rate : float
              The plus/minus deviation for interest rate. 
              E.g., if base_interest_rate=6.0 and delta_interest_rate=1.0, we range from 5.0% to 7.0%.
          - base_house_price : float
              The starting (base) house price, typically the user input.
          - delta_house_price : int
              The increment step in house price (e.g., 10,000).
          - num_price_increments : int
              Number of increments above and below the base_house_price. 
              Total points will be (2 * num_price_increments) + 1.
          - property_tax_rate : float
              The property tax rate.
          - pmi_monthly : float
              The PMI rate.

        Returns:
        --------
          An Altair chart (heatmap) showing monthly payment (color) 
          for combinations of interest rates and house prices.
        """
    
        # Range of interest rates in steps of 0.1
        lower_rate = base_interest_rate - delta_interest_rate
        higher_rate = base_interest_rate + delta_interest_rate
    
        # Generate the list of interest rates
        rates = []
        current_rate = lower_rate
        while current_rate <= higher_rate + 1e-8:
            # Round to avoid floating point drift
            rates.append(round(current_rate, 3))
            current_rate = round(current_rate + 0.1, 3)
    
        # Range of house prices in steps of delta_house_price
        # We'll go 'num_price_increments' steps below and above the base.
        # E.g. if base=300k, delta=10k, increments=5 => from 250k to 350k
        price_start = base_house_price - num_price_increments * delta_house_price
        price_end   = base_house_price + num_price_increments * delta_house_price
        prices = list(range(int(price_start), int(price_end + 1), delta_house_price))
    
        # Collect data
        records = []
        for r in rates:
            for p in prices:
                payment = calculate_monthly_housing_cost(
                    loan_amount = p,
                    annual_interest_rate = r,
                    loan_term_years = base_loan_term_years,
                    property_tax_rate = property_tax_rate,
                    pmi_rate = pmi_rate
                )
                records.append({
                    'Interest Rate (%)': r,
                    'House Price ($)': p,
                    'Monthly Payment': round(payment, 0)
                })
    
        df = pd.DataFrame(records)

        # Build an Altair heatmap
        chart = (
            alt.Chart(df)
            .mark_rect()
            .encode(
                x=alt.X(
                    'Interest Rate (%):O',  # treat them as discrete steps
                    title='Interest Rate (%)',
                    sort=rates  # ensure ascending sorting
                ),
                y=alt.Y(
                    'House Price ($):O',
                    title='House Price ($)',
                    sort="descending"
                ),
                color=alt.Color(
                    'Monthly Payment:Q',
                    title='Monthly Payment ($)',
                    scale=alt.Scale(scheme='blues')  # or 'reds', 'greens', etc.
                ),
                tooltip=[
                    alt.Tooltip('Interest Rate (%)', title='Interest Rate (%)'),
                    alt.Tooltip('House Price ($)',   title='House Price ($)', format='$,'),
                    alt.Tooltip('Monthly Payment',   title='Monthly Payment', format='$,')
                ]
            )
            .properties(
                width=800,
                height=500,
                # title='Combined Impact of Interest Rate and House Price on Monthly Payment'
            )
            .configure_title(fontSize=20)
            .configure_axis(labelFontSize=14, titleFontSize=16)
        )
    
        return mo.ui.altair_chart(
            chart,
            chart_selection="point",
            legend_selection=True,
        )

    combined_chart = plot_interest_rate_and_house_price_vs_payment(
        base_loan_term_years = loan_term.value,
        base_interest_rate = interest_rate_input.value,
        delta_interest_rate = 1.0,
        base_house_price = house_price_input.value,
        delta_house_price = 10000,
        num_price_increments = 5,
        property_tax_rate = property_tax_rate,
        pmi_rate = pmi_rate
    )

    combined_chart
    return combined_chart, plot_interest_rate_and_house_price_vs_payment


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md("""<!-- <img src="public/logo.png" width="200" /> -->""")
    return


@app.cell
def _():
    # # Create sample data
    # data = pd.DataFrame({"x": np.arange(100), "y": np.random.normal(0, 1, 100)})

    # # Create interactive chart
    # chart = mo.ui.altair_chart(
    #     (
    #         alt.Chart(data)
    #         .mark_circle()
    #         .encode(x="x", y="y", size=alt.value(100), color=alt.value("steelblue"))
    #         .properties(height=400, title="Interactive Scatter Plot")
    #     )
    # )
    # chart
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
