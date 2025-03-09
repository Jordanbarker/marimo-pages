# Marimo Pages

This repository exports my [marimo](https://marimo.io) notebooks to WebAssembly and deploys them to GitHub Pages.

## 📚 Included Pages

Currently, I just have the template examples: 
- `apps/charts.py`: Interactive data visualization with Altair
- `notebooks/fibonacci.py`: Interactive Fibonacci sequence calculator
- `notebooks/penguins.py`: Interactive data analysis with Polars and marimo

## 🧪 Testing

To test the export process, run `scripts/build.py` from the root directory.

```bash
python scripts/build.py
```

This will export all notebooks in a folder called `_site/` in the root directory. Then to serve the site, run:

```bash
python -m http.server -d _site
```

This will serve the site at `http://localhost:8000`.
