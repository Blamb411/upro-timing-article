"""
Build Word document for UPRO Timing Strategies article.
Generates individual charts from analysis data and assembles into .docx.
"""

import os
import sys
import re
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

# Add analysis script directory to path
_analysis_dir = r"C:\Users\Admin\Trading\repos\spy-80-delta\Strategies\80-Delta Call Strategy"
sys.path.insert(0, _analysis_dir)

_this_dir = os.path.dirname(os.path.abspath(__file__))
_chart_dir = os.path.join(_this_dir, "charts")
os.makedirs(_chart_dir, exist_ok=True)

# ======================================================================
# PARAMETERS (match analysis script)
# ======================================================================
INITIAL_CAPITAL = 100_000
DATA_START = "2008-01-01"
END_DATE = "2026-03-03"
TRADING_DAYS_PER_YEAR = 252

COLORS = {
    "upro_bh": "#1f77b4",
    "vix": "#d62728",
    "dual": "#2ca02c",
    "hfea": "#ff7f0e",
    "dd_exit": "#9467bd",
    "composite": "#8c564b",
    "spy": "#555555",
    "syn3x": "#17becf",
    "syn3x_m": "#bcbd22",
    "static3x": "#e377c2",
}

# ======================================================================
# DATA LOADING (reuse from analysis)
# ======================================================================

def load_data():
    """Download all needed market data."""
    print("Downloading market data...")
    tickers = {
        "SPY": "SPY", "UPRO": "UPRO", "TMF": "TMF",
        "TLT": "TLT", "VIX": "^VIX",
    }
    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start=DATA_START, end=END_DATE, progress=False, auto_adjust=True)
        data[name] = df["Close"].squeeze()
        print(f"  {name}: {len(data[name])} days")
    return data


# ======================================================================
# STRATEGY RUNNERS (simplified from main script)
# ======================================================================

def compute_metrics(values, name):
    vals = np.array(values, dtype=float)
    total_return = vals[-1] / vals[0] - 1
    n_years = len(vals) / TRADING_DAYS_PER_YEAR
    cagr = (vals[-1] / vals[0]) ** (1.0 / n_years) - 1
    daily_rets = np.diff(vals) / vals[:-1]
    sharpe = np.mean(daily_rets) / np.std(daily_rets) * np.sqrt(TRADING_DAYS_PER_YEAR) if np.std(daily_rets) > 0 else 0
    neg_rets = daily_rets[daily_rets < 0]
    sortino = np.mean(daily_rets) / np.std(neg_rets) * np.sqrt(TRADING_DAYS_PER_YEAR) if len(neg_rets) > 0 and np.std(neg_rets) > 0 else 0
    cummax = np.maximum.accumulate(vals)
    drawdowns = vals / cummax - 1
    max_dd = drawdowns.min()
    return {"name": name, "end_value": vals[-1], "cagr": cagr, "sharpe": sharpe,
            "sortino": sortino, "max_dd": max_dd}


def run_upro_bh(upro_close):
    prices = upro_close.values
    portfolio_values = (INITIAL_CAPITAL / prices[0]) * prices
    return upro_close.index, portfolio_values, compute_metrics(portfolio_values, "UPRO B&H")


def run_spy_bh(spy_close, start_date):
    spy = spy_close.loc[spy_close.index >= start_date]
    portfolio_values = (INITIAL_CAPITAL / spy.values[0]) * spy.values
    return spy.index, portfolio_values, compute_metrics(portfolio_values, "SPY B&H (1x)")


def run_synthetic_3x(spy_close, start_date, rate=0.0):
    spy = spy_close.loc[spy_close.index >= start_date]
    prices = spy.values
    daily_rets = np.diff(prices) / prices[:-1]
    daily_borrow = (rate * 2.0) / TRADING_DAYS_PER_YEAR
    pv = np.zeros(len(prices))
    pv[0] = INITIAL_CAPITAL
    for i in range(1, len(prices)):
        pv[i] = pv[i - 1] * (1 + 3.0 * daily_rets[i - 1] - daily_borrow)
        if pv[i] <= 0:
            pv[i:] = 0
            break
    label = "no cost" if rate == 0 else f"{rate:.0%} margin"
    return spy.index, pv, compute_metrics(pv, f"Synthetic 3x ({label})")


def run_static_3x(spy_close, start_date, rate=0.06, maint_margin=0.25):
    """Static 3x: $100K equity + $200K borrowed, buy $300K SPY, hold."""
    spy = spy_close.loc[spy_close.index >= start_date]
    prices = spy.values
    dates = spy.index
    equity = INITIAL_CAPITAL
    debt = equity * 2.0
    shares = (equity + debt) / prices[0]
    daily_int = rate / TRADING_DAYS_PER_YEAR
    pv = np.zeros(len(prices))
    pv[0] = equity
    margin_called = False
    for i in range(1, len(prices)):
        if margin_called:
            pv[i] = pv[i - 1]; continue
        debt *= (1.0 + daily_int)
        pos_val = shares * prices[i]
        eq = pos_val - debt
        if eq <= 0 or eq < maint_margin * pos_val:
            pv[i] = max(0.0, pos_val - debt)
            margin_called = True
        else:
            pv[i] = eq
    return dates, pv, compute_metrics(pv, f"Static 3x ({rate:.0%} margin)")


def run_vix_filter(upro_close, vix_close, threshold):
    common = upro_close.index.intersection(vix_close.index)
    upro, vix = upro_close.loc[common].values, vix_close.loc[common].values
    portfolio, shares, invested = INITIAL_CAPITAL, 0.0, False
    values, trades, days_in = [], 0, 0
    for i in range(len(upro)):
        if i == 0:
            values.append(portfolio); continue
        want_in = vix[i - 1] < threshold
        if want_in and not invested:
            shares = portfolio / upro[i]; invested = True; trades += 1
        elif not want_in and invested:
            portfolio = shares * upro[i]; shares = 0.0; invested = False
        if invested:
            values.append(shares * upro[i]); days_in += 1
        else:
            values.append(portfolio)
    return common, np.array(values), compute_metrics(values, f"VIX<{threshold}")


def run_dual_momentum(upro_close, spy_close, tlt_close, lookback=252):
    common = upro_close.index.intersection(spy_close.index).intersection(tlt_close.index)
    upro = upro_close.loc[common].values
    spy = spy_close.loc[common].values
    tlt = tlt_close.loc[common].values
    portfolio, shares, invested = INITIAL_CAPITAL, 0.0, False
    values, trades = [], 0
    for i in range(len(upro)):
        if i < lookback:
            if invested: values.append(shares * upro[i])
            else: values.append(portfolio)
            continue
        spy_mom = spy[i] / spy[i - lookback] - 1
        tlt_mom = tlt[i] / tlt[i - lookback] - 1
        want_in = spy_mom > 0 and spy_mom > tlt_mom
        if want_in and not invested:
            shares = portfolio / upro[i]; invested = True; trades += 1
        elif not want_in and invested:
            portfolio = shares * upro[i]; shares = 0.0; invested = False
        if invested: values.append(shares * upro[i])
        else: values.append(portfolio)
    return common, np.array(values), compute_metrics(values, "Dual Momentum")


def run_hfea(upro_close, tmf_close, upro_wt=0.55, rebal_days=63):
    common = upro_close.index.intersection(tmf_close.index)
    upro, tmf = upro_close.loc[common].values, tmf_close.loc[common].values
    upro_shares = (INITIAL_CAPITAL * upro_wt) / upro[0]
    tmf_shares = (INITIAL_CAPITAL * (1 - upro_wt)) / tmf[0]
    values = []
    for i in range(len(upro)):
        port_val = upro_shares * upro[i] + tmf_shares * tmf[i]
        values.append(port_val)
        if i > 0 and i % rebal_days == 0:
            upro_shares = (port_val * upro_wt) / upro[i]
            tmf_shares = (port_val * (1 - upro_wt)) / tmf[i]
    return common, np.array(values), compute_metrics(values, "HFEA 55/45")


def run_dd_exit(upro_close, threshold, cool_days):
    prices = upro_close.values
    portfolio, shares, invested = INITIAL_CAPITAL, 0.0, True
    shares = INITIAL_CAPITAL / prices[0]
    ath = prices[0]
    cool_counter = 0
    in_cool = False
    values, trades = [], 1
    for i in range(len(prices)):
        if invested:
            val = shares * prices[i]
            ath = max(ath, prices[i])
            dd = prices[i] / ath - 1
            if dd < -threshold:
                portfolio = val; shares = 0.0; invested = False
                in_cool = True; cool_counter = 0; trades += 1
            values.append(val if invested else portfolio)
        else:
            if in_cool:
                cool_counter += 1
                if cool_counter >= cool_days or prices[i] >= ath:
                    shares = portfolio / prices[i]; invested = True
                    ath = prices[i]; in_cool = False; trades += 1
            values.append(portfolio)
    name = f"DD{int(threshold*100)}%/Cool{cool_days}"
    return upro_close.index, np.array(values), compute_metrics(values, name)


def run_composite(upro_close, spy_close, vix_close, min_signals):
    common = upro_close.index.intersection(spy_close.index).intersection(vix_close.index)
    upro = upro_close.loc[common].values
    spy = spy_close.loc[common].values
    vix = vix_close.loc[common].values
    sma200 = pd.Series(spy).rolling(200).mean().values
    portfolio, shares, invested = INITIAL_CAPITAL, 0.0, False
    values, trades = [], 0
    for i in range(len(upro)):
        if i < 200:
            if invested: values.append(shares * upro[i])
            else: values.append(portfolio)
            continue
        cond_sma = spy[i - 1] > sma200[i - 1]
        cond_vix = vix[i - 1] < 25
        mom_start = max(0, i - 63)
        cond_mom = spy[i - 1] > spy[mom_start]
        n_signals = sum([cond_sma, cond_vix, cond_mom])
        want_in = n_signals >= min_signals
        if want_in and not invested:
            shares = portfolio / upro[i]; invested = True; trades += 1
        elif not want_in and invested:
            portfolio = shares * upro[i]; shares = 0.0; invested = False
        if invested: values.append(shares * upro[i])
        else: values.append(portfolio)
    return common, np.array(values), compute_metrics(values, f"Composite {min_signals}of3")


# ======================================================================
# CHART GENERATION
# ======================================================================

def chart_equity_curves(bm_dates, bm_vals, best_strats, path):
    """Chart 1: Equity curves, log scale."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(bm_dates, bm_vals, label="UPRO B&H", linewidth=2.5, color=COLORS["upro_bh"])
    strat_colors = ["vix", "dual", "hfea", "dd_exit", "composite"]
    for idx, (label, dates, vals, _) in enumerate(best_strats):
        ax.semilogy(dates, vals, label=label, linewidth=1.8, color=COLORS[strat_colors[idx]], alpha=0.85)
    ax.set_title("Portfolio Value: UPRO B&H vs. Best Timing Strategies ($100K, Log Scale)",
                 fontweight="bold", fontsize=12)
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, which="both")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def chart_drawdowns(bm_dates, bm_vals, best_strats, path):
    """Chart 2: Drawdown comparison."""
    fig, ax = plt.subplots(figsize=(10, 5))
    bm_cm = np.maximum.accumulate(bm_vals)
    bm_dd = (bm_vals / bm_cm - 1) * 100
    ax.fill_between(bm_dates, bm_dd, 0, alpha=0.25, color=COLORS["upro_bh"], label="UPRO B&H")
    # Only show DD Exit for clarity
    for label, dates, vals, _ in best_strats:
        if "DD Exit" in label:
            v = np.array(vals)
            cm = np.maximum.accumulate(v)
            dd = (v / cm - 1) * 100
            ax.plot(dates, dd, label=label, linewidth=1.5, color=COLORS["dd_exit"])
    ax.set_title("Drawdown Over Time: UPRO B&H vs. DD25%/Cool40", fontweight="bold", fontsize=12)
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def chart_risk_return(bm_metrics, all_results, path):
    """Chart 3: Risk/return scatter."""
    fig, ax = plt.subplots(figsize=(10, 7))
    # Benchmark star
    ax.scatter(abs(bm_metrics["max_dd"]) * 100, bm_metrics["cagr"] * 100,
               s=200, color=COLORS["upro_bh"], marker="*", zorder=5, label="UPRO B&H")
    ax.annotate("UPRO B&H", (abs(bm_metrics["max_dd"]) * 100, bm_metrics["cagr"] * 100),
                textcoords="offset points", xytext=(8, 5), fontsize=8, fontweight="bold")

    def get_color(name):
        if "VIX<" in name: return COLORS["vix"]
        if "Dual" in name: return COLORS["dual"]
        if "HFEA" in name: return COLORS["hfea"]
        if "DD" in name: return COLORS["dd_exit"]
        if "Composite" in name: return COLORS["composite"]
        return "#333"

    for m in all_results:
        c = get_color(m["name"])
        ax.scatter(abs(m["max_dd"]) * 100, m["cagr"] * 100, s=80, color=c, alpha=0.7, zorder=3)
        ax.annotate(m["name"], (abs(m["max_dd"]) * 100, m["cagr"] * 100),
                    textcoords="offset points", xytext=(5, 3), fontsize=7)

    legend_elements = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor=COLORS["upro_bh"], markersize=12, label="UPRO B&H"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["vix"], markersize=8, label="VIX Filter"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["dual"], markersize=8, label="Dual Momentum"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["hfea"], markersize=8, label="HFEA"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["dd_exit"], markersize=8, label="DD Exit"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["composite"], markersize=8, label="Composite"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8)
    ax.set_xlabel("Max Drawdown (%)", fontsize=11)
    ax.set_ylabel("CAGR (%)", fontsize=11)
    ax.set_title("Risk vs. Return: All Strategy Variants", fontweight="bold", fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def chart_leverage_comparison(spy_d, spy_v, s3_d, s3_v, s3m_d, s3m_v,
                              stat_d, stat_v, upro_d, upro_v, path):
    """Chart 4: Leverage comparison equity curves."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(spy_d, spy_v, label="SPY B&H (1x)", linewidth=2, color=COLORS["spy"])
    ax.semilogy(s3_d, s3_v, label="Synthetic 3x (no cost)", linewidth=2, color=COLORS["syn3x"], linestyle="--")
    ax.semilogy(s3m_d, s3m_v, label="Synthetic 3x (6% margin)", linewidth=2, color=COLORS["syn3x_m"], linestyle="-.")
    ax.semilogy(stat_d, stat_v, label="Static 3x (6% margin)", linewidth=2, color=COLORS["static3x"], linestyle=":")
    ax.semilogy(upro_d, upro_v, label="UPRO B&H", linewidth=2.5, color=COLORS["upro_bh"])
    ax.set_title("Leverage Comparison: Four Ways to Get 3x Exposure ($100K, Log Scale)",
                 fontweight="bold", fontsize=12)
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, which="both")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ======================================================================
# WORD DOCUMENT BUILDER
# ======================================================================

def set_cell_shading(cell, color_hex):
    """Set background shading on a table cell."""
    shading = cell._element.get_or_add_tcPr()
    shading_elm = shading.makeelement(qn('w:shd'), {
        qn('w:val'): 'clear',
        qn('w:color'): 'auto',
        qn('w:fill'): color_hex,
    })
    shading.append(shading_elm)


def add_table_from_rows(doc, headers, rows, highlight_rows=None, col_widths=None):
    """Add a formatted table to the document."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)

    # Data rows
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.size = Pt(9)
                    if highlight_rows and i in highlight_rows:
                        run.bold = True

    return table


def build_document(article_md, chart_paths):
    """Parse markdown and build Word doc with charts."""
    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.2)
    section.right_margin = Inches(1.2)

    # Style modifications
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    for level in range(1, 4):
        hs = doc.styles[f"Heading {level}"]
        hs.font.name = "Calibri"
        hs.font.color.rgb = RGBColor(0x1B, 0x3A, 0x5C)

    # ---- Parse markdown and build doc ----
    lines = article_md.split("\n")
    i = 0
    in_table = False
    table_rows = []
    table_headers = []

    # Chart placement markers: section heading -> chart key
    chart_after_section = {
        "The Benchmark: UPRO Buy-and-Hold": "equity_bh",
        "UPRO Era (2009-2026): The Best-Case Scenario": "leverage",
        "What Happens When You Don't Start at the Bottom": "margin_calls",
        "Daily-Rebalanced 3x Across History": "leverage_full",
        "Drawdown-Triggered Exit -- The Winner": "drawdowns",
        "Head-to-Head: Best of Each Strategy": ["risk_return"],
    }

    # Track which charts we've inserted after a table
    pending_chart = None
    last_heading = None

    while i < len(lines):
        line = lines[i]

        # Skip horizontal rules
        if line.strip() == "---":
            i += 1
            continue

        # Table handling
        if "|" in line and not line.strip().startswith("|--"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                # Check if next line is separator
                if i + 1 < len(lines) and re.match(r"^\|[-\s|]+\|$", lines[i + 1].strip()):
                    in_table = True
                    table_headers = cells
                    i += 2  # skip header + separator
                    table_rows = []
                    continue
                else:
                    in_table = True
                    table_headers = cells
                    i += 1
                    table_rows = []
                    continue
            else:
                table_rows.append(cells)
                i += 1
                continue
        elif in_table:
            # End of table - flush it
            in_table = False
            # Determine highlight rows
            highlights = set()
            for ri, row in enumerate(table_rows):
                if any("**" in cell for cell in row):
                    highlights.add(ri)
            # Clean bold markers from cells
            clean_rows = []
            for row in table_rows:
                clean_rows.append([c.replace("**", "") for c in row])
            clean_headers = [h.replace("**", "") for h in table_headers]

            add_table_from_rows(doc, clean_headers, clean_rows,
                                highlight_rows=highlights if highlights else None)
            doc.add_paragraph()  # spacing after table

            # Insert chart after specific tables
            if last_heading in chart_after_section:
                chart_key = chart_after_section[last_heading]
                if isinstance(chart_key, str) and chart_key in chart_paths:
                    doc.add_picture(chart_paths[chart_key], width=Inches(6))
                    last_p = doc.paragraphs[-1]
                    last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    doc.add_paragraph()
                elif isinstance(chart_key, list):
                    for ck in chart_key:
                        if ck in chart_paths:
                            doc.add_picture(chart_paths[ck], width=Inches(6))
                            last_p = doc.paragraphs[-1]
                            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            doc.add_paragraph()
                # Don't re-insert
                del chart_after_section[last_heading]

            table_rows = []
            table_headers = []
            # Don't increment i, process current line
            continue

        # Headings
        if line.startswith("# ") and not line.startswith("##"):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1
            continue

        if line.startswith("## "):
            heading_text = line[3:].strip()
            doc.add_heading(heading_text, level=1)
            last_heading = heading_text
            i += 1
            continue

        if line.startswith("### "):
            heading_text = line[4:].strip()
            doc.add_heading(heading_text, level=2)
            last_heading = heading_text
            i += 1

            # Insert chart after specific sub-headings
            if heading_text in chart_after_section:
                # Charts go after the DD exit table, handled above
                pass
            continue

        # Empty lines
        if line.strip() == "":
            i += 1
            continue

        # Bullet points
        if line.strip().startswith("- "):
            text = line.strip()[2:]
            p = doc.add_paragraph(style="List Bullet")
            _add_formatted_text(p, text)
            i += 1
            continue

        # Numbered lists
        num_match = re.match(r"^(\d+)\.\s+", line.strip())
        if num_match:
            text = line.strip()[num_match.end():]
            p = doc.add_paragraph(style="List Number")
            _add_formatted_text(p, text)
            i += 1
            continue

        # Italics-only lines (disclosure, etc.)
        if line.strip().startswith("*") and line.strip().endswith("*") and not line.strip().startswith("**"):
            p = doc.add_paragraph()
            text = line.strip().strip("*")
            run = p.add_run(text)
            run.italic = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        _add_formatted_text(p, line.strip())
        i += 1

    # Flush any remaining table
    if in_table and table_rows:
        clean_rows = [[c.replace("**", "") for c in row] for row in table_rows]
        clean_headers = [h.replace("**", "") for h in table_headers]
        highlights = {ri for ri, row in enumerate(table_rows) if any("**" in c for c in row)}
        add_table_from_rows(doc, clean_headers, clean_rows,
                            highlight_rows=highlights if highlights else None)

    # Insert drawdown chart before conclusion if not yet inserted
    if "drawdowns" in chart_paths:
        # Find a good spot -- insert before "Head-to-Head" section's chart
        pass

    return doc


def _add_formatted_text(paragraph, text):
    """Parse markdown bold/italic and add formatted runs to a paragraph."""
    # Pattern: **bold** and *italic*
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            # Handle single * italic within non-bold parts
            sub_parts = re.split(r'(\*[^*]+?\*)', part)
            for sp in sub_parts:
                if sp.startswith("*") and sp.endswith("*") and len(sp) > 2:
                    run = paragraph.add_run(sp[1:-1])
                    run.italic = True
                else:
                    if sp:
                        paragraph.add_run(sp)


# ======================================================================
# MAIN
# ======================================================================

def main():
    print("=" * 60)
    print("  Building UPRO Article Word Document")
    print("=" * 60)

    # Load data
    data = load_data()
    spy_close = data["SPY"]
    upro_close = data["UPRO"]
    tmf_close = data["TMF"]
    tlt_close = data["TLT"]
    vix_close = data["VIX"]

    # Run all strategies
    print("\nRunning strategies...")
    bm_d, bm_v, bm_m = run_upro_bh(upro_close)

    # Leverage comparison
    spy_d, spy_v, spy_m = run_spy_bh(spy_close, upro_close.index[0])
    s3_d, s3_v, s3_m = run_synthetic_3x(spy_close, upro_close.index[0], 0.0)
    s3m_d, s3m_v, s3m_m = run_synthetic_3x(spy_close, upro_close.index[0], 0.06)
    stat_d, stat_v, stat_m = run_static_3x(spy_close, upro_close.index[0], 0.06)

    # Timing strategies
    all_results = []
    best_per_strategy = []

    # VIX
    vix_results = {}
    for t in [15, 20, 25, 30]:
        d, v, m = run_vix_filter(upro_close, vix_close, t)
        vix_results[t] = (d, v, m)
        all_results.append(m)
    best_vix = max(vix_results.values(), key=lambda x: x[2]["sharpe"])
    best_per_strategy.append((f"VIX ({best_vix[2]['name']})", best_vix[0], best_vix[1], best_vix[2]))

    # Dual Momentum
    dm_d, dm_v, dm_m = run_dual_momentum(upro_close, spy_close, tlt_close)
    all_results.append(dm_m)
    best_per_strategy.append(("Dual Momentum", dm_d, dm_v, dm_m))

    # HFEA
    hf_d, hf_v, hf_m = run_hfea(upro_close, tmf_close)
    all_results.append(hf_m)
    best_per_strategy.append(("HFEA 55/45", hf_d, hf_v, hf_m))

    # Drawdown Exit
    dd_results = {}
    for thresh in [0.10, 0.15, 0.20, 0.25]:
        for cool in [20, 40, 60]:
            d, v, m = run_dd_exit(upro_close, thresh, cool)
            dd_results[(thresh, cool)] = (d, v, m)
            all_results.append(m)
    best_dd = max(dd_results.values(), key=lambda x: x[2]["sharpe"])
    best_per_strategy.append((f"DD Exit ({best_dd[2]['name']})", best_dd[0], best_dd[1], best_dd[2]))

    # Composite
    comp_results = {}
    for n in [2, 3]:
        d, v, m = run_composite(upro_close, spy_close, vix_close, n)
        comp_results[n] = (d, v, m)
        all_results.append(m)
    best_comp = max(comp_results.values(), key=lambda x: x[2]["sharpe"])
    best_per_strategy.append((f"Composite ({best_comp[2]['name']})", best_comp[0], best_comp[1], best_comp[2]))

    print("  All strategies complete.")

    # Generate individual charts
    print("\nGenerating charts...")
    chart_paths = {
        "equity_bh": os.path.join(_chart_dir, "01_equity_curves.png"),
        "leverage": os.path.join(_chart_dir, "02_leverage_comparison.png"),
        "margin_calls": os.path.join(_chart_dir, "leverage_margin_calls_summary.png"),
        "leverage_full": os.path.join(_chart_dir, "leverage_full.png"),
        "drawdowns": os.path.join(_chart_dir, "03_drawdowns.png"),
        "risk_return": os.path.join(_chart_dir, "04_risk_return.png"),
    }

    chart_equity_curves(bm_d, bm_v, best_per_strategy, chart_paths["equity_bh"])
    chart_leverage_comparison(spy_d, spy_v, s3_d, s3_v, s3m_d, s3m_v,
                              stat_d, stat_v, bm_d, bm_v, chart_paths["leverage"])
    chart_drawdowns(bm_d, bm_v, best_per_strategy, chart_paths["drawdowns"])
    chart_risk_return(bm_m, all_results, chart_paths["risk_return"])

    # Read article markdown
    article_path = os.path.join(_this_dir, "article_draft.md")
    with open(article_path, "r", encoding="utf-8") as f:
        article_md = f.read()

    # Build Word document
    print("\nBuilding Word document...")
    doc = build_document(article_md, chart_paths)

    # Save
    # Try primary name, fall back to _v2 if file is locked (e.g. open in Word)
    output_path = os.path.join(_this_dir, "UPRO_Timing_Strategies_Article.docx")
    try:
        with open(output_path, "ab") as _:
            pass
    except PermissionError:
        output_path = os.path.join(_this_dir, "UPRO_Timing_Strategies_Article_v2.docx")
        print(f"  Primary file locked, saving to: {os.path.basename(output_path)}")
    doc.save(output_path)
    print(f"\nDocument saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
