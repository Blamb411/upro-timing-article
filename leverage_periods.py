"""
Leverage strategy comparison across multiple historical periods.
Uses ^GSPC (S&P 500 index) for maximum history (1950-2026).

Strategies:
  1. S&P 500 B&H (1x)
  2. Synthetic 3x daily-rebalanced (no cost)
  3. Synthetic 3x daily-rebalanced (6% margin)
  4. Static 3x ($100K equity + $200K borrowed, hold)

Periods:
  A. Full history:     1950-01-03 to 2026-01-31
  B. Full history:     1993-01-29 to 2026-01-31 (SPY era)
  C. Dot-com + GFC:   2000-01-03 to 2009-12-31 (the lost decade)
  D. Pre-GFC peak:    2007-10-09 to 2009-03-09 (peak to trough)
  E. UPRO era:        2009-06-25 to 2026-01-31 (for comparison)
"""

import os
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import functools

print = functools.partial(print, flush=True)

_this_dir = os.path.dirname(os.path.abspath(__file__))
_chart_dir = os.path.join(_this_dir, "charts")
os.makedirs(_chart_dir, exist_ok=True)

INITIAL_CAPITAL = 100_000
TRADING_DAYS_PER_YEAR = 252

# ======================================================================
# DATA
# ======================================================================

def load_gspc():
    """Download full S&P 500 index history."""
    print("Downloading ^GSPC (S&P 500 index)...")
    df = yf.download("^GSPC", start="1949-01-01", end="2026-03-03",
                     progress=False, auto_adjust=True)
    close = df["Close"].squeeze()
    print(f"  {close.index[0].date()} to {close.index[-1].date()} ({len(close)} days)")
    return close


# ======================================================================
# STRATEGY RUNNERS
# ======================================================================

def compute_metrics(values, name):
    vals = np.array(values, dtype=float)
    # Handle margin-call wipeout (all zeros after some point)
    if vals[-1] <= 0:
        return {"name": name, "end_value": 0, "cagr": -1.0, "sharpe": 0,
                "sortino": 0, "max_dd": -1.0}
    n_years = len(vals) / TRADING_DAYS_PER_YEAR
    cagr = (vals[-1] / vals[0]) ** (1.0 / n_years) - 1 if vals[0] > 0 else 0
    daily_rets = np.diff(vals) / vals[:-1]
    # Filter out infinite/nan from zero-value periods
    valid = np.isfinite(daily_rets)
    dr = daily_rets[valid]
    sharpe = np.mean(dr) / np.std(dr) * np.sqrt(TRADING_DAYS_PER_YEAR) if len(dr) > 0 and np.std(dr) > 0 else 0
    neg = dr[dr < 0]
    sortino = np.mean(dr) / np.std(neg) * np.sqrt(TRADING_DAYS_PER_YEAR) if len(neg) > 0 and np.std(neg) > 0 else 0
    cummax = np.maximum.accumulate(vals)
    drawdowns = vals / cummax - 1
    max_dd = drawdowns.min()
    return {"name": name, "end_value": vals[-1], "cagr": cagr, "sharpe": sharpe,
            "sortino": sortino, "max_dd": max_dd}


def run_sp500_bh(prices, dates):
    """Plain S&P 500 buy-and-hold."""
    pv = (INITIAL_CAPITAL / prices[0]) * prices
    return dates, pv, compute_metrics(pv, "S&P 500 B&H (1x)")


def run_synthetic_3x(prices, dates, annual_rate=0.0):
    """Daily-rebalanced 3x."""
    daily_rets = np.diff(prices) / prices[:-1]
    daily_borrow = (annual_rate * 2.0) / TRADING_DAYS_PER_YEAR
    pv = np.zeros(len(prices))
    pv[0] = INITIAL_CAPITAL
    for i in range(1, len(prices)):
        pv[i] = pv[i - 1] * (1 + 3.0 * daily_rets[i - 1] - daily_borrow)
        if pv[i] <= 0:
            pv[i:] = 0
            break
    label = "no cost" if annual_rate == 0 else f"{annual_rate:.0%} margin"
    return dates, pv, compute_metrics(pv, f"Synthetic 3x ({label})")


def run_static_3x(prices, dates, annual_rate=0.06, maint_margin=0.25):
    """Static 3x: $100K equity + $200K borrowed, buy & hold."""
    equity = INITIAL_CAPITAL
    debt = equity * 2.0
    shares = (equity + debt) / prices[0]
    daily_int = annual_rate / TRADING_DAYS_PER_YEAR

    pv = np.zeros(len(prices))
    pv[0] = equity
    margin_called = False
    margin_call_idx = None

    for i in range(1, len(prices)):
        if margin_called:
            pv[i] = pv[i - 1]
            continue
        debt *= (1.0 + daily_int)
        pos_val = shares * prices[i]
        eq = pos_val - debt
        if eq <= 0 or eq < maint_margin * pos_val:
            pv[i] = max(0.0, pos_val - debt)
            margin_called = True
            margin_call_idx = i
        else:
            pv[i] = eq

    m = compute_metrics(pv, f"Static 3x ({annual_rate:.0%} margin)")
    m["margin_called"] = margin_called
    if margin_called:
        m["margin_call_date"] = str(dates[margin_call_idx].date())
        m["margin_call_day"] = margin_call_idx
        m["equity_at_call"] = pv[margin_call_idx]
    return dates, pv, m


# ======================================================================
# PERIOD ANALYSIS
# ======================================================================

def run_period(gspc_close, start, end, label):
    """Run all 4 leverage strategies for a given period."""
    mask = (gspc_close.index >= start) & (gspc_close.index <= end)
    subset = gspc_close.loc[mask]
    if len(subset) < 10:
        print(f"  WARNING: only {len(subset)} days for {label}, skipping")
        return None

    prices = subset.values
    dates = subset.index

    print(f"\n{'=' * 80}")
    print(f"  {label}")
    print(f"  {dates[0].date()} to {dates[-1].date()} ({len(dates)} trading days, "
          f"{len(dates)/TRADING_DAYS_PER_YEAR:.1f} years)")
    print(f"  S&P 500: {prices[0]:.2f} -> {prices[-1]:.2f} "
          f"({(prices[-1]/prices[0] - 1)*100:+.1f}%)")
    print(f"{'=' * 80}")

    results = []
    curves = {}

    # 1. S&P 500 B&H
    d, v, m = run_sp500_bh(prices, dates)
    results.append(m)
    curves["sp500"] = (d, v)

    # 2. Synthetic 3x (no cost)
    d, v, m = run_synthetic_3x(prices, dates, 0.0)
    results.append(m)
    curves["syn3x_free"] = (d, v)

    # 3. Synthetic 3x (6% margin)
    d, v, m = run_synthetic_3x(prices, dates, 0.06)
    results.append(m)
    curves["syn3x_6pct"] = (d, v)

    # 4. Static 3x (6% margin)
    d, v, m = run_static_3x(prices, dates, 0.06)
    results.append(m)
    curves["static3x"] = (d, v)

    # Print table
    print(f"\n  {'Strategy':<30} {'End Value':>14} {'CAGR':>8} {'Sharpe':>8} "
          f"{'Max DD':>8} {'Notes'}")
    print(f"  {'-'*30} {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*30}")
    for r in results:
        notes = ""
        if r.get("margin_called"):
            notes = f"MARGIN CALL on {r['margin_call_date']}"
            if r["equity_at_call"] > 0:
                notes += f" (${r['equity_at_call']:,.0f} remaining)"
            else:
                notes += " (WIPED OUT)"

        if r["end_value"] <= 0:
            print(f"  {r['name']:<30} {'$0':>14} {'N/A':>8} {'N/A':>8} "
                  f"{r['max_dd']:>7.1%} {notes}")
        else:
            print(f"  {r['name']:<30} ${r['end_value']:>13,.0f} {r['cagr']:>+7.1%} "
                  f"{r['sharpe']:>7.2f} {r['max_dd']:>7.1%} {notes}")

    return {"label": label, "start": str(dates[0].date()), "end": str(dates[-1].date()),
            "n_days": len(dates), "results": results, "curves": curves, "dates": dates}


# ======================================================================
# CHARTS
# ======================================================================

COLORS = {
    "sp500": "#555555",
    "syn3x_free": "#17becf",
    "syn3x_6pct": "#bcbd22",
    "static3x": "#e377c2",
}
LABELS = {
    "sp500": "S&P 500 B&H (1x)",
    "syn3x_free": "Synthetic 3x (no cost)",
    "syn3x_6pct": "Synthetic 3x (6% margin)",
    "static3x": "Static 3x (6% margin)",
}
STYLES = {
    "sp500": "-",
    "syn3x_free": "--",
    "syn3x_6pct": "-.",
    "static3x": ":",
}


def chart_period(period_data, filename):
    """Equity curve chart for one period."""
    curves = period_data["curves"]
    label = period_data["label"]

    fig, ax = plt.subplots(figsize=(10, 6))
    for key in ["sp500", "syn3x_free", "syn3x_6pct", "static3x"]:
        d, v = curves[key]
        # Don't plot zero-value tails (wiped out)
        mask = v > 0
        if mask.any():
            ax.semilogy(d[mask], v[mask], label=LABELS[key], linewidth=2,
                        color=COLORS[key], linestyle=STYLES[key])

    # Mark margin call if applicable
    static_m = period_data["results"][3]
    if static_m.get("margin_called"):
        mc_idx = static_m["margin_call_day"]
        mc_date = period_data["dates"][mc_idx]
        mc_val = curves["static3x"][1][mc_idx]
        if mc_val > 0:
            ax.plot(mc_date, mc_val, "rx", markersize=15, markeredgewidth=3,
                    zorder=10, label="Margin Call")

    ax.set_title(f"Leverage Comparison: {label} ($100K, Log Scale)",
                 fontweight="bold", fontsize=12)
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend(loc="best", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, which="both")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", rotation=30)

    # Format y-axis with dollar signs
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()
    path = os.path.join(_chart_dir, filename)
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Chart saved: {path}")
    return path


def chart_static3x_margin_calls(all_periods, filename):
    """Summary chart: static 3x equity across all periods, highlighting margin calls."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Static 3x Leverage Across Market Regimes ($100K Equity + $200K Borrowed)",
                 fontsize=13, fontweight="bold", y=0.98)

    period_keys = list(all_periods.keys())
    for idx, key in enumerate(period_keys[:4]):
        ax = axes[idx // 2][idx % 2]
        pd_data = all_periods[key]
        curves = pd_data["curves"]

        # Plot S&P 500 and static 3x
        d_sp, v_sp = curves["sp500"]
        d_st, v_st = curves["static3x"]

        # Normalize to $100K start for comparison
        ax.semilogy(d_sp, v_sp, label="S&P 500 (1x)", linewidth=1.5,
                    color=COLORS["sp500"])

        mask = v_st > 0
        if mask.any():
            ax.semilogy(d_st[mask], v_st[mask], label="Static 3x", linewidth=2,
                        color=COLORS["static3x"])

        # Mark margin call
        static_m = pd_data["results"][3]
        if static_m.get("margin_called"):
            mc_idx = static_m["margin_call_day"]
            mc_date = pd_data["dates"][mc_idx]
            mc_val = v_st[mc_idx] if v_st[mc_idx] > 0 else v_st[mc_idx - 1]
            ax.axvline(mc_date, color="red", linestyle="--", alpha=0.7, linewidth=1)
            ax.plot(mc_date, max(mc_val, 1), "rv", markersize=12, zorder=10)
            ax.annotate(f"Margin Call\n{static_m['margin_call_date']}",
                        xy=(mc_date, max(mc_val, 100)),
                        fontsize=8, color="red", fontweight="bold",
                        ha="center", va="bottom")

        ax.set_title(pd_data["label"], fontweight="bold", fontsize=10)
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3, which="both")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(_chart_dir, filename)
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Summary chart saved: {path}")
    return path


# ======================================================================
# MAIN
# ======================================================================

def main():
    print("=" * 80)
    print("  LEVERAGE STRATEGY COMPARISON ACROSS HISTORICAL PERIODS")
    print("=" * 80)

    gspc = load_gspc()

    # Define periods
    periods = {
        "full": ("1950-01-03", "2026-03-02", "Full History (1950-2026)"),
        "spy_era": ("1993-01-29", "2026-03-02", "SPY Era (1993-2026)"),
        "lost_decade": ("2000-01-03", "2009-12-31", "The Lost Decade (2000-2009)"),
        "gfc_peak_trough": ("2007-10-09", "2009-03-09", "GFC Peak to Trough (Oct 2007 - Mar 2009)"),
        "dotcom_crash": ("2000-03-24", "2002-10-09", "Dot-Com Crash (Mar 2000 - Oct 2002)"),
        "upro_era": ("2009-06-25", "2026-03-02", "UPRO Era (Jun 2009 - Mar 2026)"),
    }

    all_results = {}
    for key, (start, end, label) in periods.items():
        result = run_period(gspc, start, end, label)
        if result:
            all_results[key] = result

    # Generate charts
    print("\n" + "=" * 80)
    print("  GENERATING CHARTS")
    print("=" * 80)

    chart_paths = {}
    for key, data in all_results.items():
        path = chart_period(data, f"leverage_{key}.png")
        chart_paths[key] = path

    # Summary chart: 4 key periods
    summary_periods = {k: all_results[k] for k in
                       ["upro_era", "lost_decade", "gfc_peak_trough", "dotcom_crash"]
                       if k in all_results}
    chart_static3x_margin_calls(summary_periods, "leverage_margin_calls_summary.png")

    # Print consolidated summary
    print("\n\n" + "=" * 80)
    print("  CONSOLIDATED SUMMARY: STATIC 3x MARGIN CALL ANALYSIS")
    print("=" * 80)
    print(f"\n  {'Period':<40} {'Margin Call?':<15} {'Date':<15} {'S&P 500 Drop':<15}")
    print(f"  {'-'*40} {'-'*15} {'-'*15} {'-'*15}")
    for key, data in all_results.items():
        static_m = data["results"][3]
        sp_m = data["results"][0]
        mc = "YES" if static_m.get("margin_called") else "No"
        mc_date = static_m.get("margin_call_date", "N/A")
        sp_dd = f"{sp_m['max_dd']:.1%}"
        print(f"  {data['label']:<40} {mc:<15} {mc_date:<15} {sp_dd:<15}")

    print("\n" + "=" * 80)
    print("  COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
