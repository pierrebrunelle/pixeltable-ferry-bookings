"""Seed a few ferry sailings so the /sailings and /manifest routes have data to show.

Usage:
    python seed.py            # seeds the local `ferry` catalog directory
    python seed.py my_dir     # or another catalog directory you passed to `pxt schema update`
"""
import sys

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'ferry'
sailings = pxt.get_table(f'{target}/sailings')

SAILINGS = [
    {'sailing_id': 'S1001', 'route': 'Seattle-Bainbridge', 'depart_at': '2026-10-08T07:55', 'vessel': 'Wenatchee', 'pax_capacity': 2499},
    {'sailing_id': 'S1002', 'route': 'Seattle-Bainbridge', 'depart_at': '2026-10-08T09:10', 'vessel': 'Tacoma', 'pax_capacity': 2499},
    {'sailing_id': 'S1003', 'route': 'Seattle-Bremerton', 'depart_at': '2026-10-08T08:20', 'vessel': 'Kaleetan', 'pax_capacity': 1868},
    {'sailing_id': 'S1004', 'route': 'Anacortes-Friday Harbor', 'depart_at': '2026-10-08T10:15', 'vessel': 'Samish', 'pax_capacity': 1500},
    {'sailing_id': 'S1005', 'route': 'Anacortes-Friday Harbor', 'depart_at': '2026-10-08T14:35', 'vessel': 'Chelan', 'pax_capacity': 1090},
]

if sailings.count() == 0:
    sailings.insert(SAILINGS)
    print(f'inserted {len(SAILINGS)} sailings into {target}/sailings')
else:
    print(f'{target}/sailings already has {sailings.count()} rows; nothing to do')
