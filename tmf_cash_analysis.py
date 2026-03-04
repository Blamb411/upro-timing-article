"""
Quick analysis: DD25/Cool40 with TMF as cash vehicle instead of T-bills.
During cooling periods, buy TMF at open (when selling UPRO), sell TMF at open (when re-entering UPRO).
"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

INITIAL_CAPITAL = 100_000
DATA_START = "2008-01-01"
END_DATE = "2026-03-03"
TRADING_DAYS_PER_YEAR = 252


def load_data():
    tickers = {"UPRO": "UPRO", "TMF": "TMF", "TLT": "TLT", "IRX": "^IRX"}
    data = {}
    for name, ticker in tickers.items():
        df = yf.download(ticker, start=DATA_START, end=END_DATE, progress=False,
                         auto_adjust=True, multi_level_index=False)
        df = df.dropna(subset=["Close"])
        if name == "IRX":
            data[name] = df["Close"].squeeze()
        else:
            data[name] = df[["Open", "Close"]].copy()
        print(f"  {name}: {len(data[name])} days")
    return data


def get_daily_tbill_rate(irx_series):
    return (1 + irx_series / 100) ** (1 / 252) - 1


def compute_metrics(values, name, dates=None, trades=0, pct_invested=1.0):
    vals = np.array(values, dtype=float)
    n_years = len(vals) / TRADING_DAYS_PER_YEAR
    cagr = (vals[-1] / vals[0]) ** (1.0 / n_years) - 1
    daily_rets = np.diff(vals) / vals[:-1]
    sharpe = (np.mean(daily_rets) / np.std(daily_rets) * np.sqrt(TRADING_DAYS_PER_YEAR)
              if np.std(daily_rets) > 0 else 0)
    neg_rets = daily_rets[daily_rets < 0]
    sortino = (np.mean(daily_rets) / np.std(neg_rets) * np.sqrt(TRADING_DAYS_PER_YEAR)
               if len(neg_rets) > 0 and np.std(neg_rets) > 0 else 0)
    cummax = np.maximum.accumulate(vals)
    drawdowns = vals / cummax - 1
    max_dd = drawdowns.min()
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0
    return {
        "name": name, "end_value": vals[-1], "cagr": cagr, "sharpe": sharpe,
        "sortino": sortino, "max_dd": max_dd, "calmar": calmar,
        "pct_invested": pct_invested, "num_trades": trades,
    }


def run_dd_exit_tbill(upro_df, threshold, cool_days, tbill_daily):
    """Standard DD exit with T-bill cash."""
    dates = upro_df.index
    upro_open = upro_df["Open"].values
    upro_close = upro_df["Close"].values
    tbill = tbill_daily.reindex(dates).fillna(0).values

    shares = INITIAL_CAPITAL / upro_close[0]
    portfolio = INITIAL_CAPITAL
    invested = True
    ath = upro_close[0]
    cool_counter = 0
    in_cool = False
    exit_signal = False
    enter_signal = False
    values = [INITIAL_CAPITAL]
    trades = 1
    days_invested = 0

    for i in range(1, len(upro_close)):
        if exit_signal:
            portfolio = shares * upro_open[i]
            shares = 0.0
            invested = False
            exit_signal = False
            in_cool = True
            cool_counter = 0
        elif enter_signal:
            shares = portfolio / upro_open[i]
            invested = True
            enter_signal = False
            ath = upro_open[i]

        if invested:
            val = shares * upro_close[i]
            values.append(val)
            days_invested += 1
            ath = max(ath, upro_close[i])
            dd = upro_close[i] / ath - 1
            if dd < -threshold:
                exit_signal = True
                trades += 1
        else:
            portfolio *= (1 + tbill[i])
            values.append(portfolio)
            if in_cool:
                cool_counter += 1
                if cool_counter >= cool_days or upro_close[i] >= ath:
                    enter_signal = True
                    in_cool = False
                    trades += 1

    pct_inv = days_invested / max(len(values) - 1, 1)
    return dates, np.array(values), compute_metrics(
        values, f"DD25/Cool40 (T-bill cash)", dates=dates, trades=trades, pct_invested=pct_inv)


def run_dd_exit_bond(upro_df, bond_df, threshold, cool_days, bond_name="TMF"):
    """DD exit with a bond ETF as cash vehicle during cooling periods."""
    common = upro_df.index.intersection(bond_df.index)
    upro_open = upro_df.loc[common, "Open"].values
    upro_close = upro_df.loc[common, "Close"].values
    bond_open = bond_df.loc[common, "Open"].values
    bond_close = bond_df.loc[common, "Close"].values

    # Start invested in UPRO
    upro_shares = INITIAL_CAPITAL / upro_close[0]
    bond_shares = 0.0
    portfolio = INITIAL_CAPITAL
    in_upro = True
    ath = upro_close[0]
    cool_counter = 0
    in_cool = False
    exit_signal = False
    enter_signal = False
    values = [INITIAL_CAPITAL]
    trades = 1
    days_in_upro = 0

    for i in range(1, len(upro_close)):
        if exit_signal:
            portfolio = upro_shares * upro_open[i]
            upro_shares = 0.0
            bond_shares = portfolio / bond_open[i]
            in_upro = False
            exit_signal = False
            in_cool = True
            cool_counter = 0
        elif enter_signal:
            portfolio = bond_shares * bond_open[i]
            bond_shares = 0.0
            upro_shares = portfolio / upro_open[i]
            in_upro = True
            enter_signal = False
            ath = upro_open[i]

        if in_upro:
            val = upro_shares * upro_close[i]
            values.append(val)
            days_in_upro += 1
            ath = max(ath, upro_close[i])
            dd = upro_close[i] / ath - 1
            if dd < -threshold:
                exit_signal = True
                trades += 1
        else:
            val = bond_shares * bond_close[i]
            values.append(val)
            if in_cool:
                cool_counter += 1
                if cool_counter >= cool_days or upro_close[i] >= ath:
                    enter_signal = True
                    in_cool = False
                    trades += 1

    pct_inv = days_in_upro / max(len(values) - 1, 1)
    return common, np.array(values), compute_metrics(
        values, f"DD25/Cool40 ({bond_name} cash)", dates=common, trades=trades, pct_invested=pct_inv)


def run_upro_bh(upro_df):
    closes = upro_df["Close"].values
    portfolio_values = (INITIAL_CAPITAL / closes[0]) * closes
    dates = upro_df.index
    return dates, portfolio_values, compute_metrics(
        portfolio_values, "UPRO B&H", dates=dates, trades=1, pct_invested=1.0)


def main():
    print("Loading data...")
    data = load_data()
    upro_df = data["UPRO"]
    tmf_df = data["TMF"]
    tlt_df = data["TLT"]
    irx_series = data["IRX"]
    tbill_daily = get_daily_tbill_rate(irx_series)

    print("\nRunning strategies...")
    bh_d, bh_v, bh_m = run_upro_bh(upro_df)
    tb_d, tb_v, tb_m = run_dd_exit_tbill(upro_df, 0.25, 40, tbill_daily)
    tmf_d, tmf_v, tmf_m = run_dd_exit_bond(upro_df, tmf_df, 0.25, 40, "TMF")
    tlt_d, tlt_v, tlt_m = run_dd_exit_bond(upro_df, tlt_df, 0.25, 40, "TLT")

    # Print comparison
    print("\n" + "=" * 85)
    print(f"  {'Strategy':<30s} {'End Value':>12s} {'CAGR':>8s} {'Sharpe':>8s} "
          f"{'Sortino':>8s} {'MaxDD':>8s} {'Calmar':>8s}")
    print("-" * 85)
    for m in [bh_m, tb_m, tlt_m, tmf_m]:
        print(f"  {m['name']:<30s} ${m['end_value']:>11,.0f} {m['cagr']:>7.1%} "
              f"{m['sharpe']:>7.3f} {m['sortino']:>7.3f} {m['max_dd']:>7.1%} "
              f"{m['calmar']:>7.2f}")
    print("=" * 85)

    # Differences
    print(f"\n  TLT cash vs T-bill cash: {tlt_m['end_value']/tb_m['end_value'] - 1:+.1%} terminal wealth")
    print(f"  TMF cash vs T-bill cash: {tmf_m['end_value']/tb_m['end_value'] - 1:+.1%} terminal wealth")
    print(f"  TLT cash vs B&H:         {tlt_m['end_value']/bh_m['end_value'] - 1:+.1%} terminal wealth")
    print(f"  TMF cash vs B&H:         {tmf_m['end_value']/bh_m['end_value'] - 1:+.1%} terminal wealth")

    # Chart: equity curves
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.semilogy(bh_d, bh_v, label=f"UPRO B&H (Sharpe {bh_m['sharpe']:.2f})",
                linewidth=2, color="#1f77b4")
    ax.semilogy(tb_d, tb_v, label=f"DD25/Cool40 T-bill cash (Sharpe {tb_m['sharpe']:.2f})",
                linewidth=2, color="#9467bd")
    ax.semilogy(tlt_d, tlt_v, label=f"DD25/Cool40 TLT cash (Sharpe {tlt_m['sharpe']:.2f})",
                linewidth=2, color="#2ca02c")
    ax.semilogy(tmf_d, tmf_v, label=f"DD25/Cool40 TMF cash (Sharpe {tmf_m['sharpe']:.2f})",
                linewidth=2, color="#d62728")
    ax.set_title("DD25%/Cool40: Bond Cash Alternatives ($100K, Log Scale)",
                 fontweight="bold", fontsize=13)
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, which="both")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    chart_path = "charts/bond_cash_comparison.png"
    plt.savefig(chart_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n  Chart saved: {chart_path}")

    # Show cash period returns for both TLT and TMF
    print("\n  Cash period returns (bond ETF holding periods):")
    print(f"  {'Period':<30s} {'Days':>5s} {'TLT':>10s} {'TMF':>10s}")
    print("  " + "-" * 60)
    common_dates = upro_df.index.intersection(tmf_df.index).intersection(tlt_df.index)
    upro_close = upro_df.loc[common_dates, "Close"].values

    in_upro = True
    ath = upro_close[0]
    cool_counter = 0
    in_cool = False
    exit_signal = False
    enter_signal = False
    cash_start = None

    for i in range(1, len(upro_close)):
        if exit_signal:
            in_upro = False
            exit_signal = False
            in_cool = True
            cool_counter = 0
            cash_start = common_dates[i]
        elif enter_signal:
            if cash_start is not None:
                dt = common_dates[i]
                days = (dt - cash_start).days
                tlt_s = tlt_df.loc[cash_start, "Open"] if cash_start in tlt_df.index else None
                tlt_e = tlt_df.loc[dt, "Open"] if dt in tlt_df.index else None
                tlt_ret = (tlt_e / tlt_s - 1) * 100 if tlt_s and tlt_e else 0
                tmf_s = tmf_df.loc[cash_start, "Open"] if cash_start in tmf_df.index else None
                tmf_e = tmf_df.loc[dt, "Open"] if dt in tmf_df.index else None
                tmf_ret = (tmf_e / tmf_s - 1) * 100 if tmf_s and tmf_e else 0
                period = f"{cash_start.strftime('%Y-%m-%d')} -> {dt.strftime('%Y-%m-%d')}"
                print(f"  {period:<30s} {days:>5d} {tlt_ret:>+9.1f}% {tmf_ret:>+9.1f}%")
            in_upro = True
            enter_signal = False
            ath = upro_close[i]
            cash_start = None

        if in_upro:
            ath = max(ath, upro_close[i])
            dd = upro_close[i] / ath - 1
            if dd < -0.25:
                exit_signal = True
        else:
            if in_cool:
                cool_counter += 1
                if cool_counter >= 40 or upro_close[i] >= ath:
                    enter_signal = True
                    in_cool = False


if __name__ == "__main__":
    main()
