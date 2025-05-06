import marimo

__generated_with = "0.13.5"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import math
    import numpy as np
    import polars as pl
    import matplotlib.pyplot as plt
    return math, mo, np, pl, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # Marimo Quick Reference Notes:

    ## Getting Started
    [Installation](https://docs.marimo.io/getting_started/installation/)
    ```
    marimo edit
    ```

    ```
    marimo run notebook.py
    ```
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## KaTeX / LaTeX

    Inline:
    $f(x) = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \ldots$

    $$
    \mathbf{y} = \mathbf{X} \boldsymbol{\beta} + \boldsymbol{\varepsilon}
    $$


    \[
        \min_{\boldsymbol{\beta} \in \mathbb{R}^p} 
        \left\{\sum_{i=1}^n 
            \left( y_i - \mathbf{x}_i^\top \boldsymbol{\beta} \right)^2 
            + \lambda \sum_{j=1}^p \left| \beta_j \right| \right\}
    \]
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    slider = mo.ui.slider(1, 10)
    number = mo.ui.number(start=1, stop=10, step=1)
    checkbox = mo.ui.checkbox(label="")
    text = mo.ui.text(placeholder="type some text ...")
    text_area = mo.ui.text_area(placeholder="type some text ...")
    dropdown = mo.ui.dropdown(["a", "b", "c"])
    run_button = mo.ui.run_button(label="click me")
    date = mo.ui.date()
    file_upload = mo.ui.file(kind="area")

    array = mo.ui.array([
        mo.ui.text(), 
        mo.ui.text(), 
        mo.ui.text()
    ])

    mo.md("## UI Elements")
    return (
        array,
        checkbox,
        date,
        dropdown,
        file_upload,
        number,
        run_button,
        slider,
        text,
        text_area,
    )


@app.cell
def _(
    array,
    checkbox,
    date,
    dropdown,
    file_upload,
    mo,
    number,
    run_button,
    slider,
    text,
    text_area,
):
    mo.md(
        f"""
    mo.ui.slider: {slider} {"💵" * slider.value}

    mo.ui.dropdown: {dropdown}

    mo.ui.checkbox: {checkbox}

    mo.ui.run_button: {run_button} ➡️ {run_button.value}

    mo.ui.date: {date}

    mo.ui.number: {number}

    mo.ui.text: {text}

    mo.ui.text_area: {text_area}

    mo.ui.file: {file_upload}

    mo.ui.array: {array}
    """
    )
    return


@app.cell
def _(mo):
    grid = mo.vstack([
        mo.hstack([
            mo.ui.text(label="text 1"), 
            mo.ui.text(label="text 2")
        ]),
        mo.hstack([
            mo.ui.text(label="text 3"), 
            mo.ui.text(label="text 4")
        ]),
    ]).center()

    mo.md(
        f"""
        ## hstack and vstack
        {grid}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    justify = mo.ui.dropdown(
        ["start", "center", "end", "space-between", "space-around"],
        value="space-between",
        label="justify",
    )
    align = mo.ui.dropdown(
        ["start", "center", "end", "stretch"], value="center", label="align"
    )
    gap = mo.ui.number(start=0, step=0.25, stop=2, value=0.5, label="gap")
    wrap = mo.ui.checkbox(label="wrap")
    size = mo.ui.slider(label="box size", start=60, stop=500)

    mo.vstack([
        mo.hstack([justify, align, gap, wrap], justify="center"),
        size.center()
    ])
    return align, gap, justify, size, wrap


@app.cell(hide_code=True)
def _(mo, size):
    def create_box(num=1):
        box_size = size.value + num * 10
        return mo.Html(
            f"""
            <div style='min-width: {box_size}px; 
                min-height: {box_size}px; 
                background-color: orange; 
                text-align: center; 
                line-height: {box_size}px'>
                {str(num)}
            </div>
            """
        )


    boxes = [create_box(i) for i in range(1, 5)]
    return (boxes,)


@app.cell
def _(align, boxes, gap, justify, mo, wrap):
    mo.hstack(
        boxes,
        align=align.value,
        justify=justify.value,
        gap=gap.value,
        wrap=wrap.value,
    )
    return


@app.cell
def _(align, boxes, gap, mo):
    mo.vstack(
        boxes,
        align=align.value,
        gap=gap.value,
    )
    return


@app.cell
def _(mo):
    _t1 = mo.ui.text(label="T1 text")

    _t2 = mo.hstack([
        mo.ui.text(label="T2 text 1"),
        mo.ui.text(label="T2 text 2"),
    ])

    mo.vstack([
        mo.md("## Tabs"),
        mo.ui.tabs({
            "Tab 1": _t1,
            "Tab 2": _t2,
        })
    ])
    return


@app.cell
def _(mo):
    callout_kind = mo.ui.dropdown(
        ["neutral", "warn", "success", "info", "danger"], value="neutral"
    )
    return (callout_kind,)


@app.cell(hide_code=True)
def _(callout_kind, mo):
    mo.vstack([
        mo.md(f"## Callout"),
        mo.md(
        f"""
        **Callout**: {callout_kind}
        """
        ).callout(kind=callout_kind.value),
        mo.md(f"## Accordion"),
        mo.accordion({
                "mo.accordion": (
                    """
                    Underscore-prefixed variables are local to cells:
                    ```
                    _local_var
                    ```
                    """
                ),
                "mo.accordion 2": (
                    """
                    Text
                    """
                ),
        })
    ])



    return


@app.cell
def _(mo, np, pl):
    x = np.linspace(0, 1, 3)
    y = np.sin(x)
    df = pl.DataFrame({"x": x, "sin(x)": y})

    mo.md(
        f'''
        ## DataFrames
        {mo.as_html(df)}
        '''
    )
    return


@app.cell
def _(math, mo, np, plt):
    amplitude = mo.ui.slider(1, 2, step=0.1, label="amplitude: ")
    period = mo.ui.slider(
        math.pi / 4,
        4 * math.pi,
        value=2 * math.pi,
        step=math.pi / 8,
        label="period: ",
    )

    @mo.cache
    def plot_sin(amplitude, period):
        x = np.linspace(0, 2 * np.pi, 256)
        plt.plot(x, amplitude * np.sin(2 * np.pi / period * x))
        plt.ylim(-2.2, 2.2)
        return plt.gca()

    mo.md(
        f"""
        ## Plotting

        **Params:**
        <br>{amplitude} 
        <br>{period}
        """
    )
    return amplitude, period, plot_sin


@app.cell
def _(amplitude, mo, period, plot_sin):
    mo.md(
        rf"""
    \[
    f(x) = {amplitude.value}\sin((2\pi/{period.value:0.2f})x),
    \]

    {mo.as_html(plot_sin(amplitude.value, period.value))}
    """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
