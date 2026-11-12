#!/usr/bin/env python3
"""Builds the Paydar calculator pages (tools/<slug>/index.html), tools/index.html and sitemap.xml.

    python3 tools/_build.py

Calculator logic is in tools.js (keyed by `tool`). Files starting with "_" are not published.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://paydarapp.com'
LEGAL = 'https://avihaihemo.github.io/apps/paydar'
STORE = 'https://apps.apple.com/us/app/paydar-hours-tracker-pay/id6821644227'
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def field(id_, label, value='', kind='number', attrs='step="0.01" min="0" inputmode="decimal"', prefix=''):
    pre = f'<span class="pre">{prefix}</span>' if prefix else ''
    return (f'<label class="f"><span>{label}</span><span class="in">{pre}'
            f'<input id="{id_}" type="{kind}" value="{value}" {attrs if kind == "number" else ""}></span></label>')


def out(id_, label, strong=False, row_id=''):
    rid = f' id="{row_id}"' if row_id else ''
    cls = ' class="total"' if strong else ''
    return f'<div{rid}{cls}><dt>{label}</dt><dd id="{id_}">–</dd></div>'


def day_grid(prefix, defaults):
    cells = ''.join(
        f'<label class="day"><span>{d}</span><input id="{prefix}{i}" type="number" value="{defaults[i]}" '
        f'step="0.25" min="0" max="24" inputmode="decimal"></label>' for i, d in enumerate(DAYS))
    return f'<div class="days">{cells}</div>'


RATE = field('rate', 'Hourly rate', '20', prefix='$')

PAGES = [
    {
        'slug': 'overtime-calculator', 'tool': 'overtime',
        'title': 'Overtime Calculator: Weekly and Daily Overtime Pay',
        'h1': 'Overtime calculator',
        'desc': 'Free overtime calculator. Enter your hours for each day and your hourly rate to see regular, time-and-a-half and double-time pay. Federal, California, Alaska and Colorado rules.',
        'lede': 'Enter the hours you worked each day. The calculator splits them into regular, time-and-a-half and double-time hours and shows your gross pay for the week.',
        'form': RATE + '''<label class="f"><span>Overtime rule</span><span class="in"><select id="rule">
<option value="us">Federal: over 40 hours a week</option>
<option value="ca">California: over 8 a day, over 40 a week</option>
<option value="ak">Alaska: over 8 a day, over 40 a week</option>
<option value="co">Colorado: over 12 a day, over 40 a week</option></select></span></label>
<p class="lab">Hours worked each day</p>''' + day_grid('d', [8, 9, 8, 10, 9, 0, 0]),
        'result': out('o-reg', 'Regular') + out('o-ot', 'Overtime ×1.5') + out('o-dt', 'Double time ×2', row_id='row-dt')
                  + out('o-total', 'Gross pay this week', True) + out('o-premium', 'Overtime premium (the extra half)'),
        'cta': 'Paydar does this for every shift as you clock in and out, then checks the total against your paystub.',
        'body': '''<h2>How overtime is calculated</h2>
<p>Under the federal Fair Labor Standards Act, most hourly workers earn at least 1.5 times their regular rate for every hour over 40 in a workweek. Federal law counts the week, not the day: a 12-hour shift is not overtime by itself unless the week goes over 40.</p>
<p>Some states add daily overtime:</p>
<ul>
<li><strong>California:</strong> 1.5× after 8 hours in a day and for the first 8 hours on the seventh day in a row of the workweek; 2× after 12 hours in a day and after 8 hours on that seventh day.</li>
<li><strong>Alaska:</strong> 1.5× after 8 hours in a day or 40 in a week.</li>
<li><strong>Colorado:</strong> 1.5× after 12 hours in a day, 12 hours in a row, or 40 in a week.</li>
</ul>
<p>An hour is only counted as overtime once. If a California shift is already paid at 1.5× for running past 8 hours, those hours are not added again to the weekly 40.</p>''',
        'faq': [
            ('How do I calculate time and a half?', 'Multiply your hourly rate by 1.5. At $20 an hour, overtime pays $30 an hour. Five overtime hours add $150 to the week.'),
            ('Is overtime after 8 hours or 40 hours?', 'Federal law uses 40 hours in a workweek. California, Alaska and a few other states also pay overtime after 8 hours in one day. Choose your rule in the calculator above.'),
            ('Does a two-week pay period change overtime?', 'No. Overtime is worked out one workweek at a time. Working 30 hours one week and 50 the next means 10 overtime hours, even though the two weeks average 40.'),
            ('What is the overtime premium?', 'It is the extra half on top of your regular rate. At $20 an hour the premium is $10 for each overtime hour. For tax years 2025 to 2028, the US "no tax on overtime" deduction applies to this premium part, up to a yearly limit.'),
        ],
    },
    {
        'slug': 'time-card-calculator', 'tool': 'timecard',
        'title': 'Time Card Calculator: Hours Worked and Pay, With Breaks',
        'h1': 'Time card calculator',
        'desc': 'Free time card calculator. Enter clock-in and clock-out times and unpaid breaks for each day to get total hours, decimal hours, overtime and gross pay.',
        'lede': 'Enter when you started and finished each day, and any unpaid break. You get total hours in hours and minutes, in decimals, and your gross pay.',
        'form': RATE + '<div class="tc"><div class="tc-h"><span></span><span>In</span><span>Out</span><span>Break (min)</span><span>Hours</span></div>'
                + ''.join(
                    f'<div class="tc-r"><span>{d}</span><input id="in{i}" type="time" value="{"09:00" if i < 5 else ""}" aria-label="{d} clock in">'
                    f'<input id="out{i}" type="time" value="{"17:30" if i < 5 else ""}" aria-label="{d} clock out">'
                    f'<input id="br{i}" type="number" value="{30 if i < 5 else ""}" min="0" step="1" inputmode="numeric" aria-label="{d} break minutes">'
                    f'<b id="t{i}">–</b></div>' for i, d in enumerate(DAYS)) + '</div>',
        'result': out('o-hm', 'Total hours') + out('o-dec', 'Decimal hours') + out('o-ot', 'Over 40 this week')
                  + out('o-total', 'Gross pay', True),
        'cta': 'Skip the typing: Paydar clocks you in with one tap, or by itself when you arrive at work, and keeps the timesheet for you.',
        'body': '''<h2>How to work out hours from a time card</h2>
<p>Subtract the start time from the end time, then take off unpaid breaks. A shift from 9:00 AM to 5:30 PM with a 30-minute lunch is 8 hours. A shift that ends after midnight is handled too: 10:00 PM to 6:00 AM is 8 hours.</p>
<h2>Minutes to decimal hours</h2>
<p>Payroll uses decimal hours. Divide the minutes by 60: 15 minutes is 0.25, 30 minutes is 0.5, 45 minutes is 0.75. So 7 hours 45 minutes is 7.75 hours, not 7.45.</p>''',
        'faq': [
            ('How do I convert minutes to decimal hours?', 'Divide the minutes by 60. 20 minutes is 0.33 hours, 40 minutes is 0.67 hours, 50 minutes is 0.83 hours.'),
            ('Are breaks paid?', 'Under federal rules, short rest breaks of about 5 to 20 minutes are paid. Meal breaks of 30 minutes or more can be unpaid if you are fully relieved of work. Enter only unpaid breaks in the calculator.'),
            ('Does this calculator include overtime?', 'It pays hours over 40 in the week at 1.5 times your rate, which is the federal rule. For daily overtime in California, Alaska or Colorado, use the overtime calculator.'),
        ],
    },
    {
        'slug': 'paycheck-checker', 'tool': 'paycheck',
        'title': 'Is My Paycheck Right? Check Your Pay Against Your Hours',
        'h1': 'Is my paycheck right?',
        'desc': 'Free paycheck checker for hourly workers. Enter your hours, rate and the gross pay on your paystub to see if money is missing, and how many hours it adds up to.',
        'lede': 'Enter the hours you worked in each week of the pay period and the gross pay printed on your paystub. You will see what you should have earned and the gap, if there is one.',
        'form': RATE + field('w1', 'Hours worked, week 1', '44', attrs='step="0.25" min="0" inputmode="decimal"')
                + field('w2', 'Hours worked, week 2 (leave 0 if paid weekly)', '40', attrs='step="0.25" min="0" inputmode="decimal"')
                + field('tips', 'Tips paid through payroll (optional)', '', prefix='$')
                + field('paid', 'Gross pay on your paystub', '1650', prefix='$'),
        'result': out('o-expected', 'You should have earned') + out('o-ot', 'Overtime hours') + out('o-paid', 'Your paystub says', True),
        'verdict': True,
        'cta': 'Paydar keeps your hours as you work, so when the paystub arrives the check takes ten seconds and shows the likely cause.',
        'body': '''<h2>Compare gross pay, not take-home</h2>
<p>Use the <strong>gross pay</strong> line on your stub: the amount before taxes and deductions. Take-home pay depends on your tax withholding and benefits, so it cannot be checked from hours alone.</p>
<h2>The most common reasons a paycheck is short</h2>
<ul>
<li><strong>Hours missing:</strong> a shift, or the time before clock-in and after clock-out, never reached payroll.</li>
<li><strong>Overtime paid at the regular rate,</strong> or two weeks averaged together so that no week shows more than 40 hours.</li>
<li><strong>Time clock rounding</strong> that always rounds in the employer's favor.</li>
<li><strong>A break deducted automatically</strong> on days you worked through it.</li>
<li><strong>The wrong rate</strong> after a raise, or a missing shift differential.</li>
</ul>
<h2>What to do if money is missing</h2>
<p>Most gaps are mistakes, and payroll will fix them when you show your own record. Bring the dates, your clock-in and clock-out times and the amount. If it is not corrected, the US Department of Labor's Wage and Hour Division and your state labor office take complaints at no cost. This page gives estimates, not legal advice.</p>''',
        'faq': [
            ('How do I know if my paycheck is correct?', 'Multiply your regular hours by your rate, add overtime hours at 1.5 times the rate, and compare the result with the gross pay on your paystub. They should match to the cent, or within a few cents when hours are rounded.'),
            ('Can my employer average my hours over two weeks?', 'Not for overtime. Under federal law each workweek stands alone. 50 hours in one week is 10 overtime hours even if you worked 30 the week before.'),
            ('How far back can I claim unpaid wages?', 'Under federal law it is generally two years, or three years if the violation was willful. Some states allow longer. That is one reason to keep your own record of hours.'),
        ],
    },
    {
        'slug': 'time-clock-rounding-calculator', 'tool': 'rounding',
        'title': '7-Minute Rule Calculator: Time Clock Rounding and Your Pay',
        'h1': 'Time clock rounding calculator',
        'desc': 'See how time clock rounding (the 7-minute rule) changes your paid time. Enter your real clock-in and clock-out to see the rounded punch and what it costs or adds per year.',
        'lede': 'Many employers round punches to the nearest quarter hour. Enter your real times to see the rounded shift and what the difference is worth over a year.',
        'form': RATE + field('in', 'You clocked in at', '08:53', kind='time') + field('out', 'You clocked out at', '17:06', kind='time')
                + '''<label class="f"><span>Rounding</span><span class="in"><select id="step">
<option value="15">Nearest 15 minutes (7-minute rule)</option><option value="6">Nearest 6 minutes (tenth of an hour)</option>
<option value="5">Nearest 5 minutes</option></select></span></label>'''
                + field('shifts', 'Shifts like this per week', '5', attrs='step="1" min="1" max="7" inputmode="numeric"'),
        'result': out('o-rin', 'Rounded clock-in') + out('o-rout', 'Rounded clock-out') + out('o-actual', 'Time you worked')
                  + out('o-rounded', 'Time you are paid for'),
        'verdict_rounding': True,
        'cta': 'Paydar records your real punches and shows what rounding takes or adds in every pay period.',
        'body': '''<h2>What the 7-minute rule is</h2>
<p>With quarter-hour rounding, a punch from 1 to 7 minutes past the quarter is rounded down, and a punch from 8 to 14 minutes is rounded up. Clocking in at 8:53 counts as 9:00; clocking in at 8:52 counts as 8:45.</p>
<h2>Is time clock rounding legal?</h2>
<p>Federal rules allow rounding to the nearest 5 minutes, tenth of an hour or quarter hour, as long as it averages out so that workers are paid for all the time they work. Rounding that only goes one way, such as always rounding a late clock-out down but never rounding an early clock-in back, does not meet that test. Some states are stricter.</p>
<p>The way to know is to keep your real times next to the paid times for a few pay periods. If the difference is against you nearly every shift, raise it with payroll.</p>''',
        'faq': [
            ('What is the 7-minute rule?', 'It is quarter-hour rounding. Up to 7 minutes past the quarter hour is rounded down, and 8 minutes or more is rounded up to the next quarter hour.'),
            ('Can my employer round my time?', 'Yes under federal rules, if the rounding is neutral: over time it must not leave you paid for less time than you worked.'),
            ('How much can rounding cost?', 'Losing 7 minutes a shift at $20 an hour is $2.33. Over 5 shifts a week for a year that is about $607.'),
        ],
    },
    {
        'slug': 'tip-out-calculator', 'tool': 'tipout',
        'title': 'Tip Out Calculator for Servers and Bartenders',
        'h1': 'Tip out calculator',
        'desc': 'Free tip out calculator for servers and bartenders. Enter your tips, sales and tip-out percentages to see what you keep and your real hourly pay for the shift.',
        'lede': 'Enter tonight\'s tips and sales and your restaurant\'s tip-out percentages. You will see what goes to each role, what you keep and what the shift paid per hour.',
        'form': field('tips', 'Total tips', '240', prefix='$') + field('sales', 'Your sales', '1400', prefix='$')
                + ''.join(
                    f'<div class="pair"><label class="f"><span>{name}</span><span class="in"><input id="pct-{k}" type="number" value="{v}" step="0.5" min="0" inputmode="decimal"><span class="pre">%</span></span></label>'
                    f'<label class="f"><span>of</span><span class="in"><select id="base-{k}"><option value="sales"{" selected" if b == "sales" else ""}>sales</option><option value="tips"{" selected" if b == "tips" else ""}>tips</option></select></span></label></div>'
                    for k, name, v, b in [('a', 'Bar', 1, 'sales'), ('b', 'Busser', 1.5, 'sales'), ('c', 'Host / food runner', 5, 'tips')])
                + field('rate', 'Hourly wage', '5.50', prefix='$') + field('hours', 'Hours worked', '6', attrs='step="0.25" min="0" inputmode="decimal"'),
        'result': out('o-a', 'Bar') + out('o-b', 'Busser') + out('o-c', 'Host / food runner') + out('o-out', 'Total tip out')
                  + out('o-keep', 'Tips you keep') + out('o-wage', 'Wages') + out('o-total', 'Shift total', True) + out('o-hourly', 'Real hourly pay'),
        'cta': 'Paydar logs cash and card tips and tip-outs with each shift, and checks card tips against your paystub.',
        'body': '''<h2>How tip out works</h2>
<p>Tip out is the share of your tips that goes to the people who support your tables: bartenders, bussers, hosts and food runners. Restaurants set it as a percentage of your <strong>sales</strong> or of your <strong>tips</strong>. A sales-based tip out is the same amount on a slow-tipping night, so it takes a larger share of what you earned.</p>
<h2>Rules worth knowing</h2>
<ul>
<li>Under federal law, managers, supervisors and owners cannot take any part of a tip pool.</li>
<li>If your employer pays the lower tipped wage ($2.13 federal minimum), your wage plus tips must still reach the full minimum wage for the hours you worked. If it does not, the employer owes the difference.</li>
<li>Tips you receive on cards are paid through payroll and show on your paystub. Cash tips usually do not, so keep your own record.</li>
</ul>''',
        'faq': [
            ('What is a normal tip out percentage?', 'It varies by restaurant. Common ranges are 1 to 3 percent of sales, or 15 to 30 percent of tips, split between bar, bussers and hosts.'),
            ('Is tip out based on sales or tips?', 'Either. Check your restaurant\'s policy and pick "sales" or "tips" for each role in the calculator.'),
            ('Can my manager be in the tip pool?', 'No. Federal law bars managers and supervisors from keeping any part of employees\' tips.'),
        ],
    },
    {
        'slug': 'nanny-pay-calculator', 'tool': 'nanny',
        'title': 'Nanny Pay Calculator: Guaranteed Hours and Overtime',
        'h1': 'Nanny pay calculator',
        'desc': 'Free nanny pay calculator. Enter your hourly rate, guaranteed hours and hours worked to see weekly pay, the guaranteed-hours top-up and overtime over 40 hours.',
        'lede': 'Enter your rate, the guaranteed hours in your agreement and the hours you worked this week. The calculator shows what the family owes for the week.',
        'form': field('rate', 'Hourly rate', '25', prefix='$')
                + field('guaranteed', 'Guaranteed hours per week', '40', attrs='step="0.5" min="0" inputmode="decimal"')
                + field('worked', 'Hours worked this week', '46', attrs='step="0.25" min="0" inputmode="decimal"')
                + '<label class="check"><input id="livein" type="checkbox"> Live-in nanny (no federal overtime; some states still require it)</label>',
        'result': out('o-paidhours', 'Hours paid') + out('o-topup', 'Guaranteed-hours top-up') + out('o-ot', 'Overtime ×1.5')
                  + out('o-total', 'Pay this week', True) + out('o-year', 'At this rate for 52 weeks'),
        'cta': 'Paydar tracks guaranteed hours and overtime for each family and makes a weekly report PDF you can send them.',
        'body': '''<h2>Guaranteed hours</h2>
<p>Guaranteed hours mean you are paid for a set number of hours each week, even when the family sends you home early or goes on vacation. It is a term of your work agreement, not a law, so it should be written down. If you work fewer hours than the guarantee, you are paid the guarantee. If you work more, you are paid for the hours you worked.</p>
<h2>Nanny overtime</h2>
<p>Nannies are hourly employees under the Fair Labor Standards Act. A live-out nanny earns 1.5 times the hourly rate for hours over 40 in a week. A flat weekly salary does not remove overtime. Live-in nannies are exempt from federal overtime, but several states, including California and New York, have their own overtime rules for them.</p>
<p>Guaranteed hours that you did not work do not count toward the 40-hour overtime threshold; only hours worked do.</p>''',
        'faq': [
            ('Do nannies get overtime?', 'Yes. Live-out nannies must be paid 1.5 times their hourly rate for hours over 40 in a workweek under federal law.'),
            ('Can a nanny be paid a salary?', 'A nanny can be paid the same amount each week, but the law still treats the job as hourly. The agreement should state the hourly rate and the overtime rate that the weekly amount is made of.'),
            ('What are guaranteed hours for a nanny?', 'A promise in the work agreement to pay for a fixed number of hours each week, whether or not the family uses all of them.'),
        ],
    },
]


def head(title, desc, path, depth, extra=''):
    up = '../' * depth
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}/{path}">
<meta name="apple-itunes-app" content="app-id=6821644227">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{BASE}/{path}">
<meta property="og:image" content="{BASE}/img/shot-03.jpg">
<link rel="icon" href="{up}icon.png">
<link rel="stylesheet" href="{up}style.css">
<link rel="stylesheet" href="{up}tools/tools.css">
{extra}</head>
<body>
<header class="top"><a class="brand" href="{up or './'}"><img src="{up}icon.png" alt="" width="32" height="32">Paydar</a>
<a class="get" href="{STORE}">Get the app</a></header>
'''


def cta(text):
    return f'''<aside class="cta"><img src="../../icon.png" alt="" width="56" height="56">
<div><strong>Let your phone keep the record.</strong><p>{text}</p>
<a class="btn" href="{STORE}">Get Paydar for iPhone</a><span class="muted small">Try 7 days free</span></div></aside>'''


def foot(depth):
    up = '../' * depth
    return f'''<p class="muted small">Estimates only. Not legal, tax or financial advice. Wage rules vary by state and job.</p>
<footer>© 2026 Avihai Hemo · <a href="{up or './'}">Paydar</a> · <a href="{up}tools/">Free calculators</a> · <a href="{LEGAL}/privacy/">Privacy</a> · <a href="{LEGAL}/support/">Support</a></footer>
</main>
</body>
</html>
'''


def page(p):
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]}
    app_ld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': p['h1'].capitalize(),
              'url': f"{BASE}/tools/{p['slug']}/", 'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Any',
              'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}}
    extra = ''.join(f'<script type="application/ld+json">{json.dumps(x)}</script>\n' for x in (faq_ld, app_ld))
    verdict = ''
    if p.get('verdict'):
        verdict = '<div id="verdict" class="verdict" hidden><strong id="o-gap"></strong><p id="o-gap-note"></p></div>'
    if p.get('verdict_rounding'):
        verdict = ('<div id="verdict" class="verdict"><strong id="o-diff"></strong>'
                   '<p>Per shift: <b id="o-shift"></b> · Per year: <b id="o-year"></b></p></div>')
    others = ''.join(f'<li><a href="../{o["slug"]}/">{o["h1"]}</a></li>' for o in PAGES if o is not p)
    faqs = ''.join(f'<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>' for q, a in p['faq'])
    return (head(p['title'] + ' | Paydar', p['desc'], f"tools/{p['slug']}/", 2, extra) + f'''<main>
<h1>{p['h1']}</h1>
<p class="lede">{p['lede']}</p>
<div class="calc">
<form data-tool="{p['tool']}" class="card">{p['form']}</form>
<div class="card result"><dl>{p['result']}</dl>{verdict}</div>
</div>
{cta(p['cta'])}
{p['body']}
<h2>Questions</h2>
{faqs}
<h2>More free calculators</h2>
<ul>{others}</ul>
<script src="../tools.js" defer></script>
''' + foot(2))


def index():
    items = ''.join(f'<a class="card tool" href="{p["slug"]}/"><strong>{p["h1"]}</strong><span class="muted">{p["lede"]}</span></a>' for p in PAGES)
    title = 'Free Pay Calculators for Hourly Workers | Paydar'
    desc = 'Free calculators for hourly workers: overtime, time card, paycheck check, time clock rounding, tip out and nanny pay.'
    return head(title, desc, 'tools/', 1) + f'''<main>
<h1>Free pay calculators</h1>
<p class="lede">Quick answers for hourly workers. No sign-up, nothing stored: the numbers stay in your browser.</p>
{items}
''' + foot(1)


def main():
    for p in PAGES:
        d = os.path.join(HERE, p['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w') as f:
            f.write(page(p))
    with open(os.path.join(HERE, 'index.html'), 'w') as f:
        f.write(index())
    urls = ['', 'tools/'] + [f"tools/{p['slug']}/" for p in PAGES] 
    with open(os.path.join(HERE, '..', 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + ''.join(f'  <url><loc>{BASE}/{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    print(f'{len(PAGES)} calculators, index and sitemap written')


if __name__ == '__main__':
    main()
