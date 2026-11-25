"""Stacked imbalance zones on NQ 1-minute bars: are they revisited, how fast, are they broken.
Input: Bars & Ticks Footprint CSV exports (BullStacks / BearStacks columns). Descriptive statistics only."""
import csv, glob, random, statistics, sys
from datetime import datetime, timedelta

folder = sys.argv[1]
symbol = sys.argv[2] if len(sys.argv) > 2 else 'NQ'
rows = {}
for f in sorted(glob.glob(folder + '/FootprintPRO_' + symbol + '_*.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        if r.get('BearStacks') is None:
            continue  # old format or truncated last line
        rows[r['Time']] = r
bars = [rows[k] for k in sorted(rows)]
for b in bars:
    b['t'] = datetime.strptime(b['Time'], '%Y-%m-%d %H:%M:%S')
    b['lo'], b['hi'] = float(b['Low']), float(b['High'])

# sessions: split on gaps >= 30 min; ET clock from the session open (first bar closes at 18:01 ET)
sessions, cur = [], [bars[0]]
for p, b in zip(bars, bars[1:]):
    if b['t'] - p['t'] >= timedelta(minutes=30):
        sessions.append(cur); cur = []
    cur.append(b)
sessions.append(cur)
full = [s for s in sessions if len(s) >= 1300 and sum(int(b['Volume']) for b in s) > 300000]

def et(b, s):
    off = ((s[0]['t'].hour - 18 + 12) % 24) - 12  # local minus ET hours, from the 18:01 ET first bar
    return b['t'] - timedelta(hours=off)

def rth(t):
    m = t.hour * 60 + t.minute
    return 9 * 60 + 31 <= m <= 16 * 60

def follow(s, i, lo, hi, bull):
    """Bars after the zone's bar: when price leaves the zone, when it comes back, whether it trades through it."""
    left = None
    for j in range(i + 1, len(s)):
        b = s[j]
        touch = b['lo'] <= hi and b['hi'] >= lo
        if left is None:
            if not touch:
                left = j
            continue
        if touch:
            broke = None
            for k in range(j, len(s)):  # broken = trades beyond the far side (below a buyer zone, above a seller zone)
                if (bull and s[k]['lo'] < lo) or (not bull and s[k]['hi'] > hi):
                    broke = k; break
            c = float(b['Close'])
            react = 'held' if ((bull and c > hi) or (not bull and c < lo)) else ('broke' if ((bull and c < lo) or (not bull and c > hi)) else 'inside')
            return dict(left=True, back=j - i, broke=(broke - i) if broke is not None else None, react=react)
    return dict(left=left is not None, back=None, broke=None)

random.seed(7)
out, base = [], []
for s in full:
    for i, b in enumerate(s):
        for col, bull in (('BullStacks', True), ('BearStacks', False)):
            for z in filter(None, b[col].split('|')):
                lo, hi = map(float, z.split('-'))
                r = follow(s, i, lo, hi, bull)
                r.update(bull=bull, rth=rth(et(b, s)), size=round((hi - lo) / 0.25) + 1,
                         session_left=len(s) - 1 - i, date=et(b, s).date())
                out.append(r)
                # baseline: a zone of the same height placed at a random price inside the same bar
                h = hi - lo
                if b['hi'] - b['lo'] >= h:
                    ticks = int(round((b['hi'] - b['lo'] - h) / 0.25))
                    blo = b['lo'] + 0.25 * random.randint(0, ticks)
                    rb = follow(s, i, blo, blo + h, bull)
                    rb.update(bull=bull, rth=rth(et(b, s)))
                    base.append(rb)

def summary(name, z):
    n = len(z)
    if not n:
        return
    left = [r for r in z if r['left']]
    back = [r['back'] for r in left if r['back'] is not None]
    broke = [r for r in left if r['broke'] is not None]
    def pct(a, b): return f"{100 * a / b:.0f} %" if b else '-'
    buckets = [(1, 5), (6, 15), (16, 60), (61, 10**9)]
    bk = ' · '.join(f"{a}-{b if b < 10**9 else '+'}: {pct(sum(a <= x <= b for x in back), len(left))}" for a, b in buckets)
    print(f"{name}: zones {n}; price left the zone {pct(len(left), n)}; came back in the same session "
          f"{pct(len(back), len(left))} (median {statistics.median(back) if back else '-'} bars, {bk}); "
          f"traded through it later {pct(len(broke), len(left))}")
    rs = [r['react'] for r in left if r['back'] is not None]
    print('    first return bar closes: back on the zone side', pct(rs.count('held'), len(rs)), '| beyond the zone', pct(rs.count('broke'), len(rs)), '| inside', pct(rs.count('inside'), len(rs)))

print('bars', len(bars), 'sessions kept', len(full), full[0][0]['Time'], '->', full[-1][-1]['Time'])
summary('ALL', out)
summary('Buyer stacks', [r for r in out if r['bull']])
summary('Seller stacks', [r for r in out if not r['bull']])
summary('Formed in RTH', [r for r in out if r['rth']])
summary('Formed overnight', [r for r in out if not r['rth']])
summary('3 levels', [r for r in out if r['size'] == 3])
summary('4+ levels', [r for r in out if r['size'] >= 4])
summary('BASELINE random same-size zone in the same bar', base)
summary('BASELINE RTH', [r for r in base if r['rth']])
per_day = {}
for r in out: per_day[r['date']] = per_day.get(r['date'], 0) + 1
print('zones per session: median', statistics.median(per_day.values()), 'min', min(per_day.values()), 'max', max(per_day.values()))
