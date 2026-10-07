"""Ferry Booking API built with Pixeltable.

Two tables (sailings, bookings) with the fare, deck class and booking id as computed columns,
served as a REST API by a single FastAPIRouter: insert, update, delete, compute (quote) and
query routes (POST, GET, one-row lookups).

Layout: udfs.py (UDFs) -> models.py (tables) -> queries.py (@pxt.query) -> app.py (routes).

Run locally:
    pxt schema update app.py ferry
    pxt service run app.py ferry

See README.md for the walkthrough and Pixeltable Cloud deployment.
"""
from pixeltable.serving import FastAPIRouter

from models import Bookings, Sailings, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import booking_by_lead, manifest, sailings_on_route

booking_api = FastAPIRouter(name='booking_api')

booking_api.add_insert_route(
    Bookings,
    path='/bookings',
    inputs=[Bookings.sailing_id, Bookings.lead_name, Bookings.party_size, Bookings.vehicle_len_m,
            Bookings.extras, Bookings.status],
    outputs=[Bookings.booking_id, Bookings.fare, Bookings.deck_class, Bookings.extras, Bookings.extras_order],
)
booking_api.add_update_route(
    Bookings,
    path='/bookings/update',
    inputs=[Bookings.status, Bookings.party_size],
    outputs=[Bookings.booking_id, Bookings.status, Bookings.party_size, Bookings.fare],
)
booking_api.add_delete_route(Bookings, path='/bookings/cancel')
booking_api.add_compute_route(
    Bookings,
    path='/quote',
    inputs=[Bookings.party_size, Bookings.vehicle_len_m, Bookings.extras],
    outputs=[Bookings.fare, Bookings.deck_class],
)
booking_api.add_query_route(path='/manifest', query=manifest)
booking_api.add_query_route(path='/manifest-get', query=manifest, method='get')
booking_api.add_query_route(path='/booking/by-lead', query=booking_by_lead, one_row=True, method='get')
booking_api.add_query_route(path='/sailings', query=sailings_on_route, method='get')
booking_api.add_compute_route(Bookings, path='/quote-v2', inputs=[Bookings.party_size, Bookings.vehicle_len_m],
                              outputs=[Bookings.fare])
