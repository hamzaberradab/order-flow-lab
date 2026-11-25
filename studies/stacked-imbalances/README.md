# What happens when price comes back to a stacked imbalance?

NQ 12-26 (42 sessions, 15 Sep to 13 Nov 2026) and ES 12-26 (43 sessions, 11 Sep to 13 Nov 2026), 1-minute bars with
Tick Replay. 2,322 stacked imbalance zones: 3 or more consecutive prices with an imbalance on the same side
(Bars & Ticks Footprint defaults: diagonal ratio 4, minimum volume 10, 3 stacked levels, 1 tick per row).

| | NQ stacked | NQ random | ES stacked | ES random |
|---|---|---|---|---|
| Price came back in the same session | 88 % | 88 % | 89 % | 90 % |
| Median bars before the return | 7 | 7 | 8 | 8 |
| First return bar closes back on the zone side | 48 % | 50 % | 41 % | 41 % |

Same picture for buyer and seller stacks, RTH and overnight, 3 levels and 4+ levels: see
[`results-2026-11-17.txt`](results-2026-11-17.txt).

Reading: a stacked imbalance shows where aggressive traders hit several prices in a row. On these samples it did not
tell whether price would react there later, any more than a random price of the same bar.

Limits: two markets, one contract month, 1-minute bars only, about two months. Other timeframes, markets or a
different imbalance ratio may behave differently: run the script on your own data and tell us.

Full write-up: https://barsandticks.com/blog/do-stacked-imbalances-act-as-support
