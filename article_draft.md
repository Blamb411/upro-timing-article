# UPRO Without the Wipeout: 5 Timing Strategies That Cut Drawdowns by 40%

## Summary

- UPRO has turned $100K into $10.2M since 2009 -- roughly 100x. But its -77% maximum drawdown means a $1M portfolio drops to $230K, and most investors bail out long before the recovery.
- A leverage comparison reveals UPRO's hidden costs: a frictionless 3x position would have returned $22.6M, while 3x via margin yields only $3.1M. A static margin account avoids the -77% drawdown but would be margin-called in any period that doesn't start at a market bottom.
- I backtested 5 timing strategies across 16+ years of actual UPRO data (2009-2026, $100K starting capital): VIX filter, dual momentum, HFEA (UPRO/TMF), drawdown-triggered exit, and a composite signal.
- The best risk-adjusted strategy -- a simple drawdown exit with a cooling period -- delivered a 0.88 Sharpe ratio and cut the maximum drawdown from -77% to -46%, at the cost of about 21% less terminal wealth.

---

## The Problem With UPRO

UPRO is the greatest backtest in the history of retail investing. Since its inception in June 2009, a $100,000 investment has grown to approximately $10.2 million. That's a 32.0% compound annual growth rate over 16+ years. No mainstream ETF comes close.

You already know the catch. UPRO provides 3x daily leveraged exposure to the S&P 500, and that leverage cuts both ways. During the COVID crash in March 2020, UPRO lost roughly two-thirds of its value in weeks. During the 2022 rate-hiking cycle, it drew down brutally. Over the full test period, UPRO's maximum drawdown was **-76.8%**. That's not a typo.

Here's what -77% actually feels like. Your $1 million account shows $230,000. You have no idea if it's going to $150,000 or $100,000. Every financial commentator is explaining why this time is different. Your spouse is asking questions. And the "rational" move -- hold and wait for recovery -- requires you to believe in mean reversion with absolute conviction while staring at a six-figure loss.

Most people sell at the bottom. The backtested returns assume you don't.

This article asks a simple question: can we systematically reduce UPRO's drawdowns while keeping most of the upside? Not a magic system -- a risk management framework. I tested five approaches, each using a different market signal, across 16+ years of actual UPRO price data. The results are instructive.

A quick note on mechanics: UPRO resets its 3x leverage daily, which means it's subject to volatility decay. In a choppy, sideways market, UPRO can lose money even if the S&P 500 ends up flat. This is not a set-and-forget instrument, regardless of what the long-term backtest suggests.

---

## What I Tested

I used actual UPRO daily closing prices from inception (June 25, 2009) through March 2026 -- over 16 years. Starting capital was $100,000. When a strategy signals "out," the portfolio moves to cash earning 0% (a conservative assumption; in practice you'd earn T-bill rates in a money market fund).

All signals use prior-day closing data. There is no look-ahead bias. Here are the five strategies:

**1. VIX-Based Regime Filter.** Hold UPRO only when the VIX closes below a threshold. I tested four thresholds: 15, 20, 25, and 30. The logic is simple: elevated VIX means elevated risk, so step aside.

**2. Dual Momentum.** Based on Gary Antonacci's framework: hold UPRO when SPY's trailing 12-month return is positive (absolute momentum) AND SPY is outperforming TLT (relative momentum). When either condition fails, move to cash.

**3. HFEA 55/45.** The Bogleheads "Hedgefundie's Excellent Adventure" portfolio: 55% UPRO and 45% TMF (3x long-term Treasuries), rebalanced quarterly. This isn't timing per se -- it's a diversified leveraged portfolio that relies on the negative stock-bond correlation.

**4. Drawdown-Triggered Exit.** Exit UPRO when it falls X% from its all-time high. Re-enter when it makes a new high or after a cooling period. I tested four drawdown thresholds (10%, 15%, 20%, 25%) crossed with three cooling periods (20, 40, 60 trading days) -- 12 variants total.

**5. Composite Signal.** Hold UPRO when at least N of three conditions are met: SPY above its 200-day moving average, VIX below 25, and SPY's 3-month return is positive. I tested N=2 ("2-of-3") and N=3 ("3-of-3").

| Strategy | Signal Type | Variants | What It's Trying to Capture |
|----------|------------|----------|---------------------------|
| VIX Filter | Volatility regime | 4 | Avoid high-fear environments |
| Dual Momentum | Trend + relative strength | 1 | Follow the dominant trend |
| HFEA 55/45 | Diversification | 1 | Hedge with bonds |
| Drawdown Exit | Price-based risk | 12 | Cut losses, force patience |
| Composite | Multi-factor | 2 | Combine trend, fear, momentum |

I report CAGR, Sharpe ratio (the standard measure of risk-adjusted return), Sortino ratio, maximum drawdown, number of round-trip trades, and percentage of time invested.

---

## The Benchmark: UPRO Buy-and-Hold

First, let's be clear about what we're trying to beat -- and what we're not.

| Metric | UPRO Buy & Hold |
|--------|----------------|
| End Value | $10,161,341 |
| CAGR | +32.0% |
| Sharpe Ratio | 0.80 |
| Sortino Ratio | 0.99 |
| Max Drawdown | -76.8% |
| Trades | 1 |

These are extraordinary numbers. No timing strategy in this analysis beats buy-and-hold on total return. If you have the iron stomach to hold through a -77% drawdown -- and I mean genuinely hold, not just say you would in a hypothetical -- then buy-and-hold is the mathematically optimal choice.

But an important caveat: this test period is overwhelmingly bullish. UPRO's inception happened to coincide with the beginning of the longest bull market in American history. Every timing strategy that says "hold UPRO most of the time" will look great in a period that is almost entirely up. We don't have actual UPRO data for 2000-2009, which would have been devastating.

The major drawdown events visible in the data -- the 2011 debt ceiling crisis, the late-2018 Fed tightening scare, the 2020 COVID crash, and the 2022 rate-hiking bear market -- each inflicted serious damage on UPRO holders. The question is whether we can navigate those periods more gracefully.

---

## The Cost of Daily Leverage: UPRO vs. Synthetic 3x SPY

Before we get to timing strategies, it's worth understanding what UPRO actually costs you relative to other ways of getting 3x exposure to the S&P 500.

I modeled four alternatives alongside UPRO buy-and-hold: a frictionless 3x daily-rebalanced position (same daily mechanics as UPRO but with zero expense ratio), a daily-rebalanced version with 6% annual borrowing cost, and -- critically -- a **static 3x leveraged position** where you invest $100K of equity, borrow $200K at 6%, buy $300K of SPY, and simply hold. Plain SPY buy-and-hold serves as the 1x baseline.

The distinction between "daily-rebalanced 3x" and "static 3x" matters enormously. UPRO and the synthetic daily-rebalanced versions reset leverage to exactly 3x every day. If your portfolio drops from $100K to $90K, the next day you have $270K of exposure (3 x $90K). Static leverage works differently: you borrow a fixed dollar amount on day one, and the effective leverage ratio drifts -- rising as the market falls (amplifying losses) and falling as the market rises (reducing upside). Most importantly, **static leverage triggers margin calls**. Under Reg T's 25% maintenance requirement, your broker will liquidate you when the S&P 500 drops roughly 11% from your entry point.

### UPRO Era (2009-2026): The Best-Case Scenario

| Strategy | End Value | CAGR | Sharpe | Max DD | Notes |
|----------|-----------|------|--------|--------|-------|
| SPY B&H (1x) | $1,003,640 | +14.9% | 0.89 | -33.7% | Unlevered baseline |
| Synthetic 3x (no cost) | $22,628,688 | +38.5% | 0.89 | -76.1% | Daily rebalanced, frictionless |
| Synthetic 3x (6% margin) | $3,072,894 | +22.8% | 0.66 | -76.4% | Daily rebalanced, with borrowing cost |
| Static 3x (6% margin) | $2,467,976 | +21.2% | 0.81 | -46.9% | No margin call (entered at market bottom) |
| UPRO B&H | $10,161,341 | +32.0% | 0.80 | -76.8% | Actual ETF |

In this best-case period -- which starts at the bottom of the financial crisis -- the static 3x position actually looks attractive: lower max drawdown (-47% vs -77%) and no margin call. But this is entirely an artifact of entry timing. By the time any crash hit, accumulated gains had de-levered the position to well below 2x, providing a massive equity buffer.

The "leverage tax" on UPRO is visible here: a frictionless 3x position would have returned $22.6M vs UPRO's $10.2M. That $12.4M gap is the cumulative cost of UPRO's 0.91% expense ratio, rebalancing slippage, and tracking error over 16+ years. Yet UPRO still crushes margin-based leverage ($3.1M for daily-rebalanced, $2.5M for static) because its embedded borrowing costs are far lower than 6% margin rates.

### What Happens When You Don't Start at the Bottom

I extended the analysis using S&P 500 index data (^GSPC) going back to 1950 to test these strategies across every major crash. The results are unambiguous: **static 3x leverage gets margin-called in every period that includes a significant bear market.**

| Period | S&P 500 Return | Static 3x Result | Margin Call Date | Equity at Liquidation |
|--------|---------------|-------------------|------------------|-----------------------|
| Full History (1950-2026) | +41,206% | Margin call | Sept 30, 1974 | $269,500 |
| SPY Era (1993-2026) | +1,468% | Margin call | Oct 7, 2008 | $168,710 |
| Lost Decade (2000-2009) | -23% | Margin call | Oct 12, 2000 | $64,537 |
| GFC Peak-to-Trough (Oct 2007 - Mar 2009) | -57% | Margin call | Jan 8, 2008 | $63,491 |
| Dot-Com Crash (Mar 2000 - Oct 2002) | -49% | Margin call | Apr 14, 2000 | $65,719 |
| UPRO Era (Jun 2009 - Mar 2026) | +648% | **No margin call** | N/A | $1,700,428 |

The pattern is striking. In five out of six test periods, the static margin account was forcibly liquidated. During the dot-com crash, the margin call came just 15 trading days after entry. During the GFC, it took about 3 months. Only the UPRO era -- which uniquely starts at a generational market bottom -- survived. And even over the full 1950-2026 history, despite the S&P 500 compounding at +8.2% annually for 76 years, the static 3x account got margin-called during the 1973-74 bear market and was stuck at $269K for the remaining 52 years while unlevered S&P 500 grew to $41.3 million.

### Daily-Rebalanced 3x Across History

The daily-rebalanced strategies can't be margin-called (leverage resets daily), but they face their own demons across longer time horizons:

| Period | S&P 500 B&H | Synthetic 3x (no cost) | Synthetic 3x (6% margin) |
|--------|-------------|----------------------|------------------------|
| Full History (1950-2026) | $41.3M / +8.2% | $20.0B / +17.4% | $2.2M / +4.1% |
| Lost Decade (2000-2009) | $77K / -2.6% | $10K / -20.5% | $3K / -29.5% |
| GFC Peak-to-Trough | $43K / -44.8% | $4.3K / -89.2% | $3.6K / -90.5% |

The frictionless 3x is extraordinary over 76 years -- $100K becomes $20.0 billion -- but it's a fantasy: no one can maintain 3x leverage for free. Add realistic 6% borrowing costs and $100K grows to just $2.2M over 76 years, barely keeping pace with the S&P 500's $41.3M at 1x. During the lost decade, daily-rebalanced 3x with costs destroyed 97% of your capital. Volatility decay in a choppy, declining market is a meat grinder for leveraged strategies.

### What This Means

**UPRO's daily reset is both its curse and its superpower.** The curse is volatility decay -- in flat or declining markets, the daily reset systematically erodes value. The superpower is that you can never be margin-called. Your broker will never force-liquidate your UPRO position at the worst possible moment. You can hold through a -77% drawdown and wait for recovery, however painful that is.

Static margin leverage avoids volatility decay but introduces a far worse risk: forced liquidation at the bottom. In five of six historical periods tested, a static 3x margin account was liquidated before it could recover.

The bottom line: if you want 3x exposure to the S&P 500, UPRO is the most practical vehicle for retail investors. The question then becomes how to manage the drawdown risk -- which is what the timing strategies below attempt to solve.

![Leverage Comparison](charts/02_leverage_comparison.png)

---

## Results: Strategy by Strategy

### VIX-Based Regime Filter

The simplest idea: when the market is scared, step aside.

The problem is that VIX is reactive, not predictive. By the time VIX spikes above 25, you've already taken the first leg of the drawdown. And VIX often stays elevated during the early stages of recovery, causing you to miss the bounce.

The best VIX variant (VIX < 30) produced a $3.7M end value with a 0.73 Sharpe and -72.7% max drawdown. You sacrifice two-thirds of the terminal wealth for a max drawdown that's only 4 percentage points better. The threshold barely filters anything -- VIX is below 30 about 94% of the time -- so you get almost all of the downside with slightly less upside.

Tighter thresholds (VIX < 20, VIX < 15) aggressively reduce the time invested but destroy returns. You end up in cash during too many good days. **Verdict: blunt instrument. Not recommended.**

### Dual Momentum

Antonacci-style momentum uses a 12-month lookback for both absolute return (is SPY going up?) and relative return (is SPY beating bonds?).

End value: $928K. CAGR: +14.3%. Sharpe: 0.58. Max drawdown: -50.7%. Only invested 63% of the time, with 76 round-trip trades.

The 12-month lookback is too slow for a 3x leveraged instrument. You're late getting out and late getting back in. The maximum drawdown improved to -51%, which is meaningful, but at the cost of missing so much upside that terminal wealth drops by over 90%. And 76 trades over 16+ years creates tax drag in a taxable account. **Verdict: too much return sacrificed for the drawdown improvement.**

### HFEA 55/45 (UPRO + TMF)

The Bogleheads community made this one famous. The idea is elegant: pair UPRO with TMF (3x leveraged long-term Treasuries) because stocks and bonds are negatively correlated. When stocks crash, bonds rally, cushioning the blow. Rebalance quarterly to maintain the 55/45 split.

End value: $3.3M. CAGR: +23.5%. Sharpe: 0.87. Sortino: 1.14. Max drawdown: -70.6%. The 66 "trades" are quarterly rebalancing events (adjusting the 55/45 allocation every ~63 trading days), not 66 round-trip trades.

HFEA actually has the best Sortino ratio in the entire analysis -- meaning it handles downside volatility particularly well relative to its upside. But the max drawdown is still -71%, which is barely better than pure UPRO.

The culprit is 2022. When the Fed started hiking aggressively, both stocks and bonds cratered simultaneously. The negative correlation that HFEA depends on simply broke. UPRO fell, and TMF fell alongside it. This is the strategy's Achilles heel, and it's not a theoretical risk -- it happened. **Verdict: interesting diversification, but the correlation assumption is fragile.**

### Drawdown-Triggered Exit -- The Winner

This is the simplest concept and it produced the best risk-adjusted results. The rule: when UPRO falls X% from its all-time high, sell everything and move to cash. Wait at least Y trading days (the "cooling period") before re-entering. Re-enter when UPRO makes a new all-time high or the cooling period expires.

I tested 12 variants (four thresholds x three cooling periods):

| Variant | End Value | CAGR | Sharpe | Max DD | Trades | % Invested |
|---------|-----------|------|--------|--------|--------|-----------|
| DD10%/Cool20 | $790K | +13.2% | 0.54 | -57.3% | 79 | 70.5% |
| DD10%/Cool40 | $1.4M | +17.1% | 0.68 | -53.8% | 61 | 63.1% |
| DD10%/Cool60 | $1.2M | +16.0% | 0.69 | -50.7% | 52 | 58.3% |
| DD15%/Cool20 | $1.8M | +18.9% | 0.65 | -50.4% | 46 | 81.1% |
| DD15%/Cool40 | $2.2M | +20.5% | 0.72 | -50.4% | 37 | 73.8% |
| DD15%/Cool60 | $432K | +9.2% | 0.44 | -43.2% | 36 | 67.0% |
| DD20%/Cool20 | $9.0M | +31.0% | 0.87 | -55.3% | 29 | 86.9% |
| DD20%/Cool40 | $5.5M | +27.2% | 0.85 | -43.2% | 24 | 80.5% |
| DD20%/Cool60 | $1.1M | +15.3% | 0.60 | -64.1% | 24 | 74.1% |
| DD25%/Cool20 | $8.5M | +30.6% | 0.84 | -58.6% | 19 | 91.7% |
| **DD25%/Cool40** | **$8.0M** | **+30.1%** | **0.88** | **-46.1%** | **16** | **86.0%** |
| DD25%/Cool60 | $1.7M | +18.4% | 0.65 | -64.3% | 16 | 80.3% |

A note on the DD15%/Cool60 anomaly: its $432K end value is dramatically worse than nearby variants ($2.2M for DD15%/Cool40, $1.8M for DD15%/Cool20). The 60-day cooling period forces cash positions through critical recovery windows -- you're sitting out during the fastest part of the bounce. This illustrates that parameter sensitivity is real. The strategy's edge comes from the specific threshold+cooling combination, not from drawdown exits as a general concept.

The standout is **DD25%/Cool40**: exit when UPRO drops 25% from its peak, wait at least 40 trading days (~2 months) before re-entering.

Why it works: the 25% threshold is wide enough to avoid whipsaws from normal UPRO volatility (this is a 3x fund -- 10-15% pullbacks happen routinely) but catches genuine bear markets. The 40-day cooling period forces patience. You don't buy the first dead-cat bounce. You wait for the storm to pass.

The trade-off is explicit: you give up $2.1 million in terminal wealth (21% of buy-and-hold's end value) in exchange for a maximum drawdown that's **30.7 percentage points better** (-46.1% vs -76.8%). The Sharpe ratio improves from 0.80 to 0.88. Only 16 trades over 16+ years -- roughly one per year. You're invested 86% of the time.

### Composite Signal

This approach requires SPY to be above its 200-day SMA, VIX below 25, and SPY's 3-month return to be positive. The 2-of-3 variant holds UPRO when at least two conditions are met; 3-of-3 requires all three.

Composite 2-of-3: $1.88M end value, +19.3% CAGR, 0.67 Sharpe, -63.7% max DD. Composite 3-of-3: $930K, +14.3% CAGR, 0.61 Sharpe, -49.2% max DD.

The 3-of-3 version gets the max drawdown down to -49%, competitive with the best drawdown-exit variants. But it sacrifices far more return and requires tracking three separate indicators. **Verdict: conceptually interesting but the drawdown exit achieves similar risk reduction with a much simpler rule.**

---

## Head-to-Head: Best of Each Strategy

| Strategy | End Value | CAGR | Sharpe | Max DD | Trades | % Invested |
|----------|-----------|------|--------|--------|--------|-----------|
| **UPRO B&H** | **$10.2M** | **+32.0%** | **0.80** | **-76.8%** | **1** | **100%** |
| VIX < 30 | $3.7M | +24.2% | 0.73 | -72.7% | 43 | 93.9% |
| Dual Momentum | $928K | +14.3% | 0.58 | -50.7% | 76 | 63.1% |
| HFEA 55/45 | $3.3M | +23.5% | 0.87 | -70.6% | 66 | 100% |
| **DD25%/Cool40** | **$8.0M** | **+30.1%** | **0.88** | **-46.1%** | **16** | **86.0%** |
| Composite 2of3 | $1.9M | +19.3% | 0.67 | -63.7% | 55 | 84.5% |

![Equity Curves](charts/01_equity_curves.png)

The risk/return scatter tells the story. DD25%/Cool40 sits in the sweet spot: it preserves 79% of buy-and-hold's terminal value while cutting the maximum drawdown nearly in half. It's the best risk-adjusted performer in the analysis.

![Risk Return Scatter](charts/04_risk_return.png)

HFEA is a respectable second on Sharpe (0.87) thanks to its strong Sortino ratio, but its -70.6% max drawdown means it didn't solve the core problem. Dual Momentum and Composite sacrifice too much return for the risk reduction they provide. The VIX filter either destroys returns (tight thresholds) or barely reduces risk (VIX < 30).

I want to be direct about something: these are in-sample results. The DD25%/Cool40 parameters were selected because they look good on this data. Out-of-sample, results will almost certainly be worse. I address this in the limitations section.

---

## How to Implement the Drawdown Exit

If you want to apply the DD25%/Cool40 strategy, here's the complete process:

1. **Track UPRO's all-time high** on a closing-price basis. Start with the current ATH.
2. **Each trading day at market close**, calculate the drawdown: (today's close / ATH) - 1.
3. **If the drawdown exceeds -25%**, sell all UPRO at the next market open. Move proceeds to a money market fund or short-term Treasuries.
4. **Start a 40-trading-day clock** (approximately 8 calendar weeks).
5. **Re-enter UPRO when either**: (a) UPRO closes at a new all-time high, or (b) 40 trading days have elapsed since your exit. Buy at the next open.
6. **Reset the ATH tracker** and repeat.

You can do this with a simple spreadsheet. Check once a day after the close. This is not day trading -- it's closer to a quarterly rebalancing discipline, just triggered by drawdowns instead of the calendar.

**Tax considerations.** Each exit is a taxable event. At roughly one trade per year, this is manageable but real. In an IRA or 401(k), it's a non-issue. In a taxable account, most exits during drawdowns will be at a loss, making them tax-loss harvesting opportunities.

**Transaction costs.** At 16 trades over 16+ years and $0 commissions at most brokers, costs are negligible.

**Cash return.** Our backtest assumes 0% on cash. In practice, money market funds yielded 5%+ in 2023-2024. This means actual results for any timing strategy would be modestly better than what we show here.

**The most important rule: don't tinker.** Pick your parameters and stick with them. If you start adjusting the threshold after a whipsaw, you've defeated the purpose of having a systematic rule.

---

## Where Are We Now?

If you had been following the DD25%/Cool40 strategy from UPRO's inception, here's your current position as of March 2, 2026:

**Status: IN (holding UPRO).** The strategy re-entered on May 7, 2025 at $69.28, after the 40-day cooling period expired following an exit triggered on March 11, 2025. That exit fired when UPRO fell 26.4% from its then-peak of $98.33. Your position is up +66.4% since re-entry.

UPRO's all-time high was $122.23 on January 12, 2026. The current price of $115.32 represents a -5.7% drawdown from that peak -- well within normal volatility and nowhere near the -25% threshold that would trigger an exit.

For context, here are the strategy's most recent signals:

- **Nov 2022:** Re-entered at $33.39 after 40-day cooling period (following the 2022 rate-hiking drawdown)
- **Oct 2023:** Exited at $37.07 (-26.5% drawdown from $50.44 peak)
- **Dec 2023:** Re-entered at $51.80 (new all-time high)
- **Mar 2025:** Exited at $72.37 (-26.4% drawdown from $98.33 peak)
- **May 2025:** Re-entered at $69.28 after 40-day cooling period

The pattern is instructive. The strategy sat out the worst of the 2022 bear market, re-entered in late 2022, caught the 2023-2024 rally, stepped aside during the early-2025 correction, and is now fully invested again. If UPRO drops 25% from its January 2026 high -- roughly below $91.67 -- the exit trigger will fire. Until then, you hold.

---

## Limitations and Honest Caveats

I want to be transparent about what this analysis can and cannot tell us.

**In-sample testing.** I selected DD25%/Cool40 as the "winner" because it performed best on the 2009-2026 data (through March 2026). The parameters were not determined independently of the test data. Out-of-sample, the edge will likely shrink. The mitigating factor: 25% and 40 days are round, intuitive numbers -- not suspiciously precise values like 23.7% and 37 days that would scream overfitting.

**Survivorship bias in the test period.** UPRO launched in June 2009, at the start of one of the greatest bull markets ever. Any strategy that says "hold UPRO most of the time" will look fantastic over this period. We cannot test against 2000-2009 with actual UPRO data, and that decade would have been devastating for leveraged long equity.

**Volatility decay is real.** We used actual UPRO prices, so the decay from daily rebalancing is embedded in the data. But over longer periods, 3x daily leverage systematically underperforms 3x the index return. This is a feature of the product, not a modeling error.

**Execution risk.** The backtest assumes execution at closing prices. In practice, you'd sell at the next open after the signal triggers, which could be materially different -- especially during the volatile markets that trigger drawdown exits in the first place.

**Psychology is the actual risk.** When UPRO is ripping higher and you're sitting in cash because of the cooling period, you will want to override the rule. When UPRO has dropped 24.5% and you haven't sold because the threshold is 25%, you will want to override the rule. The strategy only works if you follow it mechanically. History suggests most people won't.

---

## Conclusion

Simple drawdown-triggered exits can meaningfully improve UPRO's risk profile without exotic indicators, frequent trading, or complex portfolio construction. The DD25%/Cool40 rule -- exit at a 25% drawdown, wait 40 trading days before re-entering -- delivered the highest Sharpe ratio in the analysis (0.88) while cutting the maximum drawdown from -77% to -46%.

The trade-off is real: approximately 21% less terminal wealth over 16+ years. You're giving up about $2.1 million on a $100K starting portfolio. That's a lot of money. Whether it's worth it depends on whether you'd actually hold through a -77% drawdown. If the honest answer is no, then a strategy that caps your pain at -46% and keeps 79% of the upside is a rational choice.

This is not a recommendation to buy UPRO. Leveraged ETFs are inherently risky instruments with structural headwinds from volatility decay. But if you've already decided to hold UPRO -- and millions of investors have -- then managing that risk with a systematic, rules-based approach is better than managing it with your gut.

The real value of a timing strategy isn't the extra Sharpe points. It's the ability to sleep at night during a crash, knowing you have a plan and the discipline to follow it.

---

*Disclosure: I am long SPY (5,000+ shares across multiple accounts) and hold deep in-the-money SPY and QQQ LEAPS calls. I do not hold UPRO.*

*The analysis uses historical data from June 2009 through March 2026. Past performance does not guarantee future results. This article is for informational purposes only and does not constitute investment advice.*
