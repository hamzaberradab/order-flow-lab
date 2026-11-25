# Order Flow Lab

Open, reproducible studies of order flow patterns on CME index futures, by [Bars & Ticks](https://barsandticks.com).

We test the popular claims of footprint trading with counts instead of opinions, and publish the code and the
aggregated results, including the ones that do not flatter the tools we sell.

> Educational research only. Nothing here is financial advice or a trading signal. Past statistics do not predict
> future results. Trading futures involves substantial risk of loss.

## Studies

| Study | Markets | Sample | Finding | Write-up |
|---|---|---|---|---|
| [Do stacked imbalances act as support?](studies/stacked-imbalances/) | NQ, ES 1-minute | 85 sessions, 2,322 zones | On the first return, a stacked zone held about as often as a same-size zone placed at random in the same bar (NQ 48 % vs 50 %, ES 41 % vs 41 %). | [Article](https://barsandticks.com/blog/do-stacked-imbalances-act-as-support) |

## How the studies work

- **Data**: 1-minute bars built with Tick Replay in NinjaTrader 8, exported to CSV by the Bars & Ticks Footprint indicator.
  The raw market data is **not** included: exchange data cannot be redistributed. Only the code and the aggregated
  statistics are published.
- **Baseline**: every study compares the pattern with a random control drawn from the same bars, so a result only
  counts if the pattern beats chance.
- **Reproduce it**: the scripts use the Python standard library only (Python 3.9+). Point them at your own exports.

## Stacked imbalances: run it yourself

```
python studies/stacked-imbalances/stacked_study.py "<folder with the CSV exports>" NQ
python studies/stacked-imbalances/stacked_study.py "<folder with the CSV exports>" ES
```

The script reads every `FootprintPRO_<SYMBOL>_*.csv` file in the folder (the file name keeps the indicator's internal name). Columns used:
`Time` (`YYYY-MM-DD HH:MM:SS`), `High`, `Low`, `Close`, `Volume`, and `BullStacks` / `BearStacks`
(stacked zones of the bar as `low-high` price ranges separated by `|`, e.g. `21000.25-21000.75|21003-21003.5`).
Any 1-minute export with those columns works; the tick size is 0.25 (NQ, ES).

Method, in short:

1. Sessions are split on gaps of 30 minutes or more; only complete sessions are kept.
2. For each zone, the script follows the next bars of the same session: does price leave the zone, does it come back,
   how many bars later, and how the first returning bar closes (back on the zone side, beyond it, or inside).
3. The same follow-up runs on a zone of the same height placed at a random price inside the same bar (fixed seed).

Full results: [`results-2026-11-17.txt`](studies/stacked-imbalances/results-2026-11-17.txt).

## Feedback

Found a bug in a script, or ran it on another market? Open an issue. We publish corrections in the results file and in
the article.

## License

Code: MIT. Results and text: CC BY 4.0, please link back to the study.

NinjaTrader® is a registered trademark of NinjaTrader Group, LLC. Bars & Ticks is not affiliated with NinjaTrader.
