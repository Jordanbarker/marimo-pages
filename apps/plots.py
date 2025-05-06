import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Altair
        Data Types:

        - Nominal (N): categorical
        - Ordinal (O): ordered
        - Quantitative (Q): numeric
        - Temporal (T): time series
        """
    )
    return


@app.cell
def _():
    import altair as alt
    import pandas as pd
    import numpy as np
    from scipy.stats import norm

    rng = np.random.default_rng(seed=42)

    # Build dummpy time-series DataFrame
    df = pd.DataFrame(
        np.cumsum(rng.standard_normal((100, 3)), axis=0).round(2),
        columns=["A", "B", "C"],
        index=pd.date_range(start="2025-01-01", periods=100, name="ds"),
    )

    # Melt into long format
    df_long = df.reset_index().melt("ds", var_name="category", value_name="y")

    print("df_long.head():")
    print(df_long.head())

    # Selection on the nearest date
    nearest = alt.selection_point(
        nearest=True,
        on="pointerover",
        fields=["ds"],
        empty=False
    )
    when_near = alt.when(nearest).then(alt.value(1)).otherwise(alt.value(0))


    # Base line with temporal x
    line = (
        alt.Chart(df_long)
        .mark_line(interpolate="basis")
        .encode(
            x=alt.X("ds:T", title="Date"),
            y=alt.Y("y:Q", title="Value"),
            color=alt.Color("category:N", legend=None),
        )
    )

    # Points that highlight on hover
    points = line.mark_point().encode(opacity=when_near)


    # Add new categories for the rules layer
    extra_features = df_long.copy()
    extra_features["category"] = extra_features["category"] + "*2"
    extra_features["y"] = extra_features["y"] * 2
    df_long = pd.concat([df_long, extra_features])

    """
    Vertical rules at the selected date
    - transform_pivot: reshapes data by pivoting the column "category" into multiple columns using the column "y" for values.

        | ds | A   | B   | C   | A*2 | B*2 | C*2 |
        |----|-----|-----|-----|-----|-----|-----|
        | 0  | ... | ... | ... | ... | ... | ... |
        | 1  | ... | ... | ... | ... | ... | ... |
    """
    rules = (
        alt.Chart(df_long)
        .transform_pivot("category", value="y", groupby=["ds"])
        .mark_rule(color="gray") # adds vertical rule lines to the chart.
        .encode(
            x="ds:T",
            opacity=when_near,
            tooltip=[
                alt.Tooltip(c, type="quantitative") for c in sorted(df_long["category"].unique())
            ],
        )
        .add_params(nearest)
    )

    alt.layer(line, points, rules).properties(width=600, height=300)
    return alt, norm, np, pd


@app.cell(hide_code=True)
def _():
    # import altair as alt
    # import pandas as pd
    # import numpy as np

    # np.random.seed(42)
    # columns = ["A", "B", "C"]
    # source = pd.DataFrame(
    #     np.cumsum(np.random.randn(100, 3), 0).round(2),
    #     columns=columns, index=pd.RangeIndex(100, name="x"),
    # )
    # source = source.reset_index().melt("x", var_name="category", value_name="y")

    # # Create a selection that chooses the nearest point & selects based on x-value
    # nearest = alt.selection_point(nearest=True, on="pointerover",
    #                               fields=["x"], empty=False)

    # # The basic line
    # line = alt.Chart(source).mark_line(interpolate="basis").encode(
    #     x="x:Q",
    #     y="y:Q",
    #     color="category:N"
    # )
    # when_near = alt.when(nearest)

    # # Draw points on the line, and highlight based on selection
    # points = line.mark_point().encode(
    #     opacity=when_near.then(alt.value(1)).otherwise(alt.value(0))
    # )

    # # Draw a rule at the location of the selection
    # rules = alt.Chart(source).transform_pivot(
    #     "category",
    #     value="y",
    #     groupby=["x"]
    # ).mark_rule(color="gray").encode(
    #     x="x:Q",
    #     opacity=when_near.then(alt.value(0.3)).otherwise(alt.value(0)),
    #     tooltip=[alt.Tooltip(c, type="quantitative") for c in columns],
    # ).add_params(nearest)


    # # Put the five layers into a chart and bind the data
    # alt.layer(
    #     line, points, rules
    # ).properties(
    #     width=600, height=300
    # )
    return


@app.cell
def _(mo):
    age = mo.ui.slider(0, 100, step=1, value=30, label="Age: ")

    mo.md(
        """
        ## Maximum Heart-Rate Distribution

        HR<sub>max</sub> has a standard deviation ~7-11 beats/min.

        It can be predicted using the following equation:

        $$ \\text{HR}_{max} = 208 - 0.7 * \\text{age} $$


        """ + f"""<br>{age}"""
    )
    return (age,)


@app.cell(hide_code=True)
def _(age, alt, norm, np, pd):
    def heart_rate_pdf(age: int) -> pd.DataFrame:
        """Builds a normal PDF for the age-predicted maximal heart-rate.

        The mean comes from the equation HR_max = 208 − 0.7 × age, which has
        better agreement with treadmill tests than the classic 220 − age.  

        Args:
            age: Age of the individual in years.

        Returns:
            A DataFrame with columns “HR” (beats · min⁻¹) and “PDF”.
        """
        hr_mean = 208 - 0.7 * age
        hr_std = 9  # Typical population SD.  Adjust if you have cohort data.
        x = np.linspace(hr_mean - 3 * hr_std, hr_mean + 3 * hr_std, 400)

        return pd.DataFrame({"HR": x, "PDF": norm.pdf(x, hr_mean, hr_std)})


    # dynamic curve (your original code assumes an external alt.Param called "age")
    dynamic_df = heart_rate_pdf(age.value)
    dynamic_line = (
        alt.Chart(dynamic_df)
        .mark_line(strokeWidth=4)
        .encode(x=alt.X("HR:Q", title="Heart Rate (beats/min)"),
                y=alt.Y("PDF:Q", title="Density"),
                tooltip=["HR", "PDF"])
    )

    # static reference curve at age = 30
    static_df = heart_rate_pdf(30)
    static_line = (
        alt.Chart(static_df)
        .mark_line(strokeDash=[5, 5], strokeWidth=4, color="firebrick")
        .encode(x="HR:Q", y="PDF:Q")
        .transform_calculate(label='"Age 30"')  # label for legend later
    )

    # combine and add a legend that distinguishes the two
    chart = (
        (dynamic_line + static_line)
        .resolve_scale(color="independent")     # separate legend entries
        .properties(width=500, height=300,
                    title="Normal PDF of Maximal Heart-Rate\n(dynamic age vs. age 30)")
    )

    chart
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
