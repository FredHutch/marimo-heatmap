import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    with mo.status.spinner("Loading dependencies..."):
        import pandas as pd
        import seaborn as sns
        import matplotlib.pyplot as plt
        import plotly.express as px
        import io
        from typing import List
        import scipy
    return List, io, pd, plt, sns


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Simple Heatmap Display

    Input: Spreadsheet with values in long or wide form.
    """
    )
    return


@app.cell
def _(mo):
    # Ask the user to upload a spreadsheet
    upload_ui = mo.ui.file(
        label="Upload a CSV",
        kind="area",
        multiple=False
    )
    upload_ui
    return (upload_ui,)


@app.cell
def _(mo, upload_ui):
    mo.stop(len(upload_ui.value) == 0)
    # Long or wide format
    orientation = mo.ui.dropdown(label="Data Orientation:", options=["Long", "Wide"], value="Long")
    orientation
    return (orientation,)


@app.cell
def _(io, mo, orientation, pd, upload_ui):
    if orientation.value == "Long":
        long_df = pd.read_csv(io.BytesIO(upload_ui.value[0].contents))
        if long_df.shape[1] < 3:
            read_args = mo.md("Must upload table with at least three columns to plot.")
        else:
            read_args = mo.md("""
            - {index}
            - {columns}
            - {values}
            """).batch(
                index=mo.ui.dropdown(label="Rows:", options=long_df.columns.values, value=long_df.columns.values[0]),
                columns=mo.ui.dropdown(label="Columns:", options=long_df.columns.values, value=long_df.columns.values[1]),
                values=mo.ui.dropdown(label="Values:", options=long_df.columns.values, value=long_df.columns.values[2])
            )
    else:
        read_args = mo.md("")

    read_args
    return long_df, read_args


@app.cell
def _(io, long_df, orientation, pd, read_args, upload_ui):
    if orientation.value == "Long":
        wide_df = long_df.pivot(**read_args.value)
    else:
        wide_df = pd.read_csv(io.BytesIO(upload_ui.value[0].contents), index_col=0)

    wide_df
    return (wide_df,)


@app.cell
def _(mo, wide_df):
    # Plotting options
    plot_args = mo.md("""
    - {rows}
    - {cols}
    - {make_symmetrical}
    - {diagonal}
    - {show_values}
    - {fmt}
    - {sort_by_values}
    - {cmap}
    - {multiplier}
    - {width}
    - {height}
    """).batch(
        rows=mo.ui.multiselect(label="Show Rows:", options=wide_df.index.values, value=wide_df.index.values),
        cols=mo.ui.multiselect(label="Show Columns:", options=wide_df.columns.values, value=wide_df.columns.values),
        make_symmetrical=mo.ui.checkbox(label="Make Symmetrical", value=True),
        diagonal=mo.ui.number(label="Diagonal Fill Value:", value=0),
        show_values=mo.ui.checkbox(label="Show Values", value=True),
        fmt=mo.ui.text(label="Format Values:", value=""),
        sort_by_values=mo.ui.checkbox(label="Sort Table by Values", value=True),
        cmap=mo.ui.text(label="Color Map:", value="Blues"),
        multiplier=mo.ui.number(label="Multiply Values (optional):", value=1),
        width=mo.ui.number(label="Width:", value=10),
        height=mo.ui.number(label="Height:", value=10),
    )
    plot_args
    return (plot_args,)


@app.cell
def _(List, io, pd, plot_args, plt, sns, wide_df):
    def plot(
        rows: List[str],
        cols: List[str],
        make_symmetrical: bool,
        diagonal: float,
        show_values: bool,
        fmt: str,
        sort_by_values: bool,
        cmap: str,
        multiplier: float,
        width: float,
        height: float
    ):
        plot_df = wide_df.copy()
        shared_ix = list(set(rows) & set(cols))
        if make_symmetrical:
            for ix1 in shared_ix:
                for ix2 in shared_ix:
                    if pd.isnull(plot_df.loc[ix1, ix2]) and plot_df.loc[ix2, ix1] is not None:
                        plot_df.loc[ix1, ix2] = plot_df.loc[ix2, ix1]
                    elif pd.isnull(plot_df.loc[ix2, ix1]) and plot_df.loc[ix1, ix2] is not None:
                        plot_df.loc[ix2, ix1] = plot_df.loc[ix1, ix2]

        for ix in shared_ix:
            if pd.isnull(plot_df.loc[ix, ix]):
                plot_df.loc[ix, ix] = diagonal
    
        plot_df = plot_df.loc[rows, cols]

        if multiplier is not None:
            plot_df = plot_df * multiplier

        g = sns.clustermap(
            data=plot_df.fillna(0),
            row_cluster=sort_by_values,
            col_cluster=sort_by_values,
            annot=show_values,
            fmt="" if fmt is None else fmt,
            cmap=cmap,
            figsize=(width, height)
        )
        g.ax_heatmap.set_xlabel("")
        g.ax_heatmap.set_ylabel("")

        # Save the figure as png
        with io.BytesIO() as buf:
            plt.savefig(buf, format="png")
            buf.seek(0)
            png = buf.read()
        return plt.gca(), png


    gca, png = plot(**plot_args.value)
    gca
    return (png,)


@app.cell
def _(mo, png):
    mo.download(
        label="Download PNG",
        filename="heatmap.png",
        data=png
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
