import marimo

__generated_with = "0.13.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # House Affordability Calculator

    ## 28/36 Rule
    No more than **28%** of the borrower's gross monthly income should be spent on housing costs. Housing costs typically includes:

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
def _():
    import numpy as np
    import altair as alt
    import pandas as pd
    import marimo as mo

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
        alt,
        car_payments_input,
        down_payment_input,
        house_price_input,
        income_input,
        interest_rate_input,
        loan_term,
        mo,
        other_expenses_input,
        pd,
        pmi_rate,
        property_tax_rate,
        property_taxes_input,
        student_loans_input,
    )


@app.cell
def _(
    car_payments_input,
    down_payment_input,
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
    def calculate_mortgage_payment(loan_amount: float, 
                                   loan_term_years: int, 
                                   annual_interest_rate: float) -> float:
        """
        Calculates the monthly mortgage payment for a given loan amount, term, and annual interest rate.

        Args:
            loan_amount: The total principal of the loan.
            loan_term_years: The loan term in years.
            annual_interest_rate: The annual interest rate (percentage).

        Returns:
            The required monthly mortgage payment.
        """    
        monthly_interest_rate = annual_interest_rate / 100 / 12
        total_payments = loan_term_years * 12

        if monthly_interest_rate > 0:
            monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**total_payments / \
                              ((1 + monthly_interest_rate)**total_payments - 1)
        else:
            monthly_payment = loan_amount / total_payments

        return monthly_payment


    def calculate_monthly_housing_cost(
        loan_amount: float,
        annual_interest_rate: float,
        loan_term_years: int,
        property_tax_rate: float,
        pmi_rate: float
    ) -> float:
        """
        Calculates the monthly housing cost including mortgage, property tax, and PMI.

        Args:
            loan_amount: The total principal of the loan.
            annual_interest_rate: The annual interest rate (percentage).
            loan_term_years: The loan term in years.
            property_tax_rate: The annual property tax rate (as a decimal). For example, 0.02 for 2%.
            pmi_rate: The annual PMI rate (as a decimal). For example, 0.0055 for 0.55%.

        Returns:
            The monthly housing cost (mortgage + property taxes + PMI).
        """
        monthly_mortgage = calculate_mortgage_payment(loan_amount, loan_term_years, annual_interest_rate)
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
    non_housing_cost_monthly = student_loans_input.value + car_payments_input.value + other_expenses_input.value
    non_housing_cost_annual = non_housing_cost_monthly * 12

    # Total monthly expenses
    monthly_expenses = housing_cost_monthly + non_housing_cost_monthly

    # Percentages of income
    percent_income_housing = (housing_cost_annual / income_input.value) * 100
    percent_income_non_housing = (non_housing_cost_annual / income_input.value) * 100
    percent_income_total = percent_income_housing + percent_income_non_housing
    return (
        calculate_monthly_housing_cost,
        housing_cost_monthly,
        loan_amount,
        monthly_expenses,
        monthly_mortgage,
        percent_income_housing,
        percent_income_non_housing,
        percent_income_total,
        pmi_monthly,
        property_tax_monthly,
    )


@app.cell
def _(
    amortization_cumulative_chart,
    amortization_monthly_chart,
    generate_amortization_schedule,
    housing_cost_monthly,
    interest_rate_input,
    loan_amount,
    loan_term,
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
    text_36 = "**more**" if percent_income_total > 36 else "less"
    callout = "warn" if percent_income_total > 36 or percent_income_housing > 28 else "success"

    schedule_df = generate_amortization_schedule(loan_amount, interest_rate_input.value, loan_term.value)

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
            # mo.md("### Amortization Schedule"),
            mo.md("#### Monthly Principal and Interest Payments"),
            amortization_monthly_chart(schedule_df),
            mo.md("#### Cumulative Principal and Interest Payments"),
            amortization_cumulative_chart(schedule_df)])
    ], widths='equal')
    return


@app.cell
def _(alt, mo, monthly_mortgage, pd):
    def generate_amortization_schedule(loan_amount: float, 
                                       interest_rate: float, 
                                       loan_term: int) -> pd.DataFrame:
        """
        Generates a monthly amortization schedule for the given loan parameters.

        Args:
            loan_amount: The principal of the loan.
            interest_rate: The annual interest rate (percentage).
            loan_term: The loan term in years.

        Returns:
            A pandas DataFrame containing Month, Date, Principal, Interest, and Remaining Balance columns.
        """    
        amortization_schedule = []
        remaining_balance = loan_amount
        monthly_interest_rate = interest_rate / 100 / 12

        # Reference date at which the schedule starts
        start_date = pd.to_datetime("today").normalize()

        for month in range(1, loan_term * 12 + 1):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_mortgage - interest_payment
            remaining_balance -= principal_payment

            # The date for this row is the start_date plus (month - 1) months
            current_date = start_date + pd.DateOffset(months=month - 1)

            amortization_schedule.append({
                'Month': month,
                'Date': current_date,
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Remaining Balance': max(remaining_balance, 0)
            })

        schedule_df = pd.DataFrame(amortization_schedule)

        return schedule_df

    def amortization_monthly_chart(schedule_df: pd.DataFrame):
        """
        Creates an interactive Altair chart showing monthly principal and interest payments over time.

        Args:
            schedule_df: A DataFrame with monthly amortization data, including 'Date', 'Principal', and 'Interest'.

        Returns:
            A Marimo UI chart object with the Altair visualization.
        """
        # Plotting principal vs. interest over time
        chart_data = schedule_df.melt(
            'Date', 
            ['Principal', 'Interest'], 
            var_name='Payment Type', 
            value_name='Amount'
        )
        chart_data['Amount'] = chart_data['Amount'].round(2)

        # Selection that chooses the nearest point based on Date
        nearest = alt.selection_point(
            nearest=True,
            on='pointerover',
            fields=['Date'],
            empty=False
        )

        # Base chart
        base = alt.Chart(chart_data).encode(
            x=alt.X('Date:T', axis=alt.Axis(format='%B %Y')),  # Month Year
            y='Amount:Q',
            color='Payment Type:N'
        ).properties(width=350, height=200)

        # The basic line layer
        line = base.mark_line(strokeWidth=3)

        # Points that only appear on hover
        points = base.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        # Rule that shows tooltips for both principal and interest
        # We pivot the Payment Type column to have one row per Date
        rules = alt.Chart(chart_data).transform_pivot(
            'Payment Type',
            value='Amount',
            groupby=['Date']
        ).mark_rule(color='gray').encode(
            x='Date:T',
            # Show a vertical rule only on hover
            opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
            # Multi-line tooltip, formatted with commas
            tooltip=[
                alt.Tooltip('Date:T', title='Date', format='%B %Y'),
                alt.Tooltip('Principal:Q', title='Principal', format=','),
                alt.Tooltip('Interest:Q', title='Interest', format=',')
            ]
        ).add_params(nearest)

        # Layer everything and configure the legend
        monthly_chart = (
            alt.layer(line, points, rules)
            # .configure_legend(
            #     titleFontSize=14,
            #     labelFontSize=12,
            #     symbolSize=200
            # )
        )

        return mo.ui.altair_chart(monthly_chart)


    def amortization_cumulative_chart(schedule_df: pd.DataFrame):
        """
        Creates an interactive Altair chart showing the cumulative principal and interest payments over time.

        Args:
            schedule_df: A DataFrame with monthly amortization data, including 'Date', 'Principal', and 'Interest'.

        Returns:
            A Marimo UI chart object with the Altair visualization.
        """
        schedule_df['Cumulative Principal'] = schedule_df['Principal'].cumsum()
        schedule_df['Cumulative Interest'] = schedule_df['Interest'].cumsum()

        # Reshape for charting
        chart_data = schedule_df.melt(
            'Date',
            ['Cumulative Principal', 'Cumulative Interest'],
            var_name='Payment Type',
            value_name='Amount'
        )

        chart_data['Amount'] = chart_data['Amount'].round(2)

        nearest = alt.selection_point(
            nearest=True,
            on='pointerover',
            fields=['Date'],
            empty=False
        )

        # Base chart encoding
        base = alt.Chart(chart_data).encode(
            x=alt.X('Date:T', axis=alt.Axis(format='%B %Y')),
            y='Amount:Q',
            color='Payment Type:N'
        ).properties(width=350, height=200)

        # Line layer
        line = base.mark_line(strokeWidth=3)

        # Points that only appear on hover
        points = base.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        # Rule for tooltip display
        # We pivot the Payment Type column to allow for multi-line tooltip
        rules = alt.Chart(chart_data).transform_pivot(
            'Payment Type',
            value='Amount',
            groupby=['Date']
        ).mark_rule(color='gray').encode(
            x='Date:T',
            opacity=alt.condition(nearest, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip('Date:T', title='Date', format='%B %Y'),
                alt.Tooltip('Cumulative Principal:Q', title='Cumulative Principal', format=','),
                alt.Tooltip('Cumulative Interest:Q', title='Cumulative Interest', format=',')
            ]
        ).add_params(nearest)

        # Combine layers
        cumulative_chart = alt.layer(line, points, rules)

        return mo.ui.altair_chart(cumulative_chart)
    return (
        amortization_cumulative_chart,
        amortization_monthly_chart,
        generate_amortization_schedule,
    )


@app.cell
def _():
    ## What-if Analysis
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
        Plots a heatmap showing how monthly housing cost changes with variations 
        in interest rate and house price.

        Args:
            base_loan_term_years: The term of the loan in years.
            base_interest_rate: The base annual interest rate (e.g., 6.0 for 6.0%).
            delta_interest_rate: The plus/minus deviation for interest rate.
            base_house_price: The starting house price (e.g., user input).
            delta_house_price: The step increment for house price (e.g., 10000).
            num_price_increments: The number of increments above and below the base house price.
            property_tax_rate: The annual property tax rate (decimal form).
            pmi_rate: The annual PMI rate (decimal form).

        Returns:
            A Marimo UI chart object with an Altair heatmap, illustrating monthly 
            payments over a grid of interest rates and house prices.
        """
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
                    sort=rates
                ),
                y=alt.Y(
                    'House Price ($):O',
                    title='House Price ($)',
                    sort="descending"
                ),
                color=alt.Color(
                    'Monthly Payment:Q',
                    title='Monthly Payment ($)',
                    scale=alt.Scale(scheme='blues')
                ),
                tooltip=[
                    alt.Tooltip('Interest Rate (%)', title='Interest Rate (%)'),
                    alt.Tooltip('House Price ($)', title='House Price ($)', format='$,'),
                    alt.Tooltip('Monthly Payment', title='Monthly Payment', format='$,')
                ]
            )
            .properties(width=800, height=500)
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
        num_price_increments = 10,
        property_tax_rate = property_tax_rate,
        pmi_rate = pmi_rate
    )

    combined_chart
    return


@app.cell
def _():
    def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> float:
        """
        Calculates monthly mortgage payments.

        Args:
            principal: The loan amount.
            annual_rate: The annual interest rate (percentage).
            years: The loan term in years.

        Returns:
            Monthly mortgage payment.
        """
        monthly_rate = annual_rate / 100 / 12
        months = years * 12
        payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        return payment


    def evaluate_interest_buydown(
        principal: float,
        base_rate: float,
        buy_down_rate: float,
        buy_down_cost: float,
        years: int
    ) -> dict:
        """
        Evaluates whether it's worthwhile to buy down the interest rate.

        Args:
            principal: The loan amount.
            base_rate: Original annual interest rate (percentage).
            buy_down_rate: Reduced annual interest rate after buydown (percentage).
            buy_down_cost: Cost required to buy the rate down.
            years: The loan term in years.


        Returns:
            A dictionary with:
                - 'monthly_payment_current': Current monthly payment without the buydown.
                - 'monthly_payment_buydown': Monthly payment after the buydown.
                - 'monthly_savings': The difference in monthly payments.
                - 'break_even_months': How many months are needed to recoup buy_down_cost via monthly savings.
                - 'total_savings_if_held_to_term': The total savings over the entire loan term if held to maturity.
        """
        monthly_payment_current = calculate_monthly_payment(principal, base_rate, years)
        monthly_payment_buydown = calculate_monthly_payment(principal, buy_down_rate, years)
        monthly_savings = monthly_payment_current - monthly_payment_buydown

        if monthly_savings > 0:
            break_even_months = buy_down_cost / monthly_savings
        else:
            break_even_months = float('inf')  # If there's no actual savings, break-even doesn't happen

        # Total payments across the entire loan term
        total_months = years * 12
        total_savings_if_held_to_term = monthly_savings * total_months

        return {
            'monthly_payment_current': monthly_payment_current,
            'monthly_payment_buydown': monthly_payment_buydown,
            'monthly_savings': monthly_savings,
            'break_even_months': break_even_months,
            'break_even_years': break_even_months / 12,
            'total_savings_if_held_to_term': total_savings_if_held_to_term
        }

    principal = 400000
    base_rate = 7.0
    bought_rate = 6.5
    buydown_cost = 5000
    years = 30
    holding_period_years = 7

    results = evaluate_interest_buydown(
        principal, 
        base_rate, 
        buy_down_rate=bought_rate, 
        buy_down_cost=buydown_cost, 
        years=years
    )

    # for key, value in results.items():
    #     print(f"{key.replace('_', ' ').capitalize()}: {value:.2f}")
    return


@app.cell
def _(mo):
    mo.md("""<!-- <img src="public/logo.png" width="200" /> -->""")
    return


if __name__ == "__main__":
    app.run()
