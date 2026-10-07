"""Call every route of the ferry booking API, then book 12 seats in parallel.

Usage:
    python client_demo.py                          # local service (pxt service run ... --port 8000)
    python client_demo.py https://<your-service-url>  # hosted service; set PIXELTABLE_API_KEY first

Uses only the Python standard library. The API key, if any, is read from the
PIXELTABLE_API_KEY environment variable and sent as the X-api-key header.
"""
import concurrent.futures as cf
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000').rstrip('/')
API_KEY = os.environ.get('PIXELTABLE_API_KEY')


def call(method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    headers = {'Content-Type': 'application/json'}
    if API_KEY:
        headers['X-api-key'] = API_KEY
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read() or b'null')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


FAILURES: list[str] = []


def show(label: str, method: str, path: str, body: dict | None = None, expect: int = 200):
    code, out = call(method, path, body)
    print(f'{label:<34} {code}  {json.dumps(out)[:200]}')
    if code != expect:
        FAILURES.append(f'{label}: got {code}, expected {expect}')
    return out


# 1. Price a trip without storing anything (compute route)
show('quote (2 adults, 6.1 m car, cabin)', 'POST', '/quote',
     {'party_size': 2, 'vehicle_len_m': 6.1, 'extras': {'cabin': True}})

# 2. Book: the fare, deck class and booking id are computed by Pixeltable on insert
booking = show('book', 'POST', '/bookings', {
    'sailing_id': 'S1001', 'lead_name': 'Ada Lovelace', 'party_size': 3,
    'vehicle_len_m': 4.6, 'extras': {'bikes': 2}, 'status': 'held',
})
booking_id = booking.get('booking_id') if isinstance(booking, dict) else None

# 3. Update by primary key; the fare is recomputed because party_size changed
show('update (check in, 4 people)', 'POST', '/bookings/update',
     {'booking_id': booking_id, 'status': 'checked_in', 'party_size': 4})

# 4. Query routes: POST body, GET query params, and a one-row lookup (404 if absent)
show('manifest (POST)', 'POST', '/manifest', {'sailing_id': 'S1001'})
show('manifest (GET)', 'GET', '/manifest-get?sailing_id=S1001')
show('booking by lead', 'GET', '/booking/by-lead?lead_name=' + urllib.parse.quote('Ada Lovelace'))
show('booking by lead (missing -> 404)', 'GET', '/booking/by-lead?lead_name=Nobody', expect=404)
show('sailings on a route', 'GET', '/sailings?route=' + urllib.parse.quote('Seattle-Bainbridge'))

# 5. Concurrency: 12 parallel clients booking the same sailing
def book(i: int):
    return call('POST', '/bookings', {
        'sailing_id': 'S1005', 'lead_name': f'Walk-on {i:02d}', 'party_size': 1 + i % 4,
        'vehicle_len_m': None, 'extras': {'seat': i}, 'status': 'held',
    })

with cf.ThreadPoolExecutor(max_workers=12) as pool:
    codes = [code for code, _ in pool.map(book, range(12))]
print(f'{"12 parallel bookings":<34} status codes: {sorted(set(codes))}')
if set(codes) != {200}:
    FAILURES.append(f'parallel bookings: status codes {sorted(set(codes))}')
show('manifest S1005', 'POST', '/manifest', {'sailing_id': 'S1005'})

# 6. Cancel (delete route, by primary key)
show('cancel', 'POST', '/bookings/cancel', {'booking_id': booking_id})

if FAILURES:
    print('\nFAILED:', *FAILURES, sep='\n  ')
    sys.exit(1)
print('\nall routes OK')
