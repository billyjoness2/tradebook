from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import Instrument, Trade
from .serializers import TradeSerializer


class TradeSerializerTests(TestCase):

    def setUp(self):
        self.inst = Instrument.objects.create(ticker="AAPL", name="Apple", asset_class="EQUITY")

    def payload(self, **overrides):
        data = {"instrument": self.inst.id, "side": "BUY", "quantity": "5",
                "price": "10.5", "executed_at": "2026-10-02T10:00:00Z"}
        return {**data, **overrides}

    def test_valid(self):
        self.assertTrue(TradeSerializer(data=self.payload()).is_valid())

    def test_negative_quantity_rejected(self):
        s = TradeSerializer(data=self.payload(quantity="-5"))
        self.assertFalse(s.is_valid())
        self.assertIn("quantity", s.errors)


class TradeApiTests(APITestCase):
    def setUp(self):
        self.aapl = Instrument.objects.create(ticker="AAPL", name="Apple", asset_class="EQUITY")
        self.btc = Instrument.objects.create(ticker="BTC", name="Bitcoin", asset_class="CRYPTO")
        mk = lambda i, side, q, p, t: Trade.objects.create(
            instrument=i, side=side, quantity=Decimal(q), price=Decimal(p), executed_at=t)
        self.t1 = mk(self.aapl, "BUY", "10", "100", "2026-01-01T10:00:00Z")
        self.t2 = mk(self.aapl, "SELL", "4", "150", "2026-02-01T10:00:00Z")
        self.t3 = mk(self.btc, "BUY", "0.5", "60000", "2026-03-01T10:00:00Z")

    def ids(self, params):
        r = self.client.get("/trades/", params)
        self.assertEqual(r.status_code, 200, r.content)
        return [t["id"] for t in r.json()]

    # --- list / ordering
    def test_list_all_newest_first(self):
        self.assertEqual(self.ids({}), [self.t3.id, self.t2.id, self.t1.id])

    # --- exact filters
    def test_ticker(self):
        self.assertEqual(sorted(self.ids({"ticker": "AAPL"})), [self.t1.id, self.t2.id])

    def test_ticker_case_insensitive(self):
        self.assertEqual(sorted(self.ids({"ticker": "aapl"})), [self.t1.id, self.t2.id])

    def test_unknown_ticker_empty_200(self):
        self.assertEqual(self.ids({"ticker": "ZZZZ"}), [])

    def test_asset_class(self):
        self.assertEqual(self.ids({"asset_class": "CRYPTO"}), [self.t3.id])

    def test_side(self):
        self.assertEqual(sorted(self.ids({"side": "BUY"})), [self.t1.id, self.t3.id])

    def test_invalid_side_is_400(self):
        self.assertEqual(self.client.get("/trades/", {"side": "HOLD"}).status_code, 400)

    def test_combined(self):
        self.assertEqual(self.ids({"ticker": "AAPL", "side": "BUY"}), [self.t1.id])

    # --- ranges
    def test_price_min_inclusive(self):
        self.assertEqual(sorted(self.ids({"price_min": "150"})), [self.t2.id, self.t3.id])

    def test_price_max_inclusive(self):
        self.assertEqual(sorted(self.ids({"price_max": "150"})), [self.t1.id, self.t2.id])

    def test_price_exact_via_min_eq_max(self):
        self.assertEqual(self.ids({"price_min": "150", "price_max": "150"}), [self.t2.id])

    def test_price_min_zero_is_valid(self):
        self.assertEqual(len(self.ids({"price_min": "0"})), 3)

    def test_quantity_range(self):
        self.assertEqual(self.ids({"quantity_min": "1", "quantity_max": "5"}), [self.t2.id])

    def test_price_garbage_is_400(self):
        r = self.client.get("/trades/", {"price_min": "abc"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("price_min", r.json())

    def test_executed_at_datetime_range(self):
        self.assertEqual(
            self.ids({"executed_at_min": "2026-02-01T00:00:00Z", "executed_at_max": "2026-02-28T00:00:00Z"}),
            [self.t2.id])

    def test_executed_at_date_only(self):
        self.assertEqual(sorted(self.ids({"executed_at_min": "2026-02-01"})), [self.t2.id, self.t3.id])

    def test_executed_at_garbage_is_400(self):
        self.assertEqual(self.client.get("/trades/", {"executed_at_min": "banana"}).status_code, 400)

    def test_executed_at_invalid_month_is_400(self):
        self.assertEqual(self.client.get("/trades/", {"executed_at_min": "2026-13-01T00:00:00Z"}).status_code, 400)

    # --- create / detail
    def payload(self, **o):
        return {**{"instrument": self.aapl.id, "side": "BUY", "quantity": "5", "price": "10.5",
                   "executed_at": "2026-10-02T10:00:00Z"}, **o}

    def test_create_201(self):
        r = self.client.post("/trades/", self.payload(), format="json")
        self.assertEqual(r.status_code, 201, r.content)

    def test_create_negative_quantity_400(self):
        r = self.client.post("/trades/", self.payload(quantity="-5"), format="json")
        self.assertEqual(r.status_code, 400)

    def test_create_zero_price_400(self):
        self.assertEqual(self.client.post("/trades/", self.payload(price="0"), format="json").status_code, 400)

    def test_create_unknown_instrument_400(self):
        self.assertEqual(self.client.post("/trades/", self.payload(instrument=9999), format="json").status_code, 400)

    def test_detail_200_and_404(self):
        self.assertEqual(self.client.get(f"/trades/{self.t1.id}/").status_code, 200)
        self.assertEqual(self.client.get("/trades/9999/").status_code, 404)

    def test_patch_and_delete(self):
        r = self.client.patch(f"/trades/{self.t1.id}/", {"quantity": "11"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.client.delete(f"/trades/{self.t1.id}/").status_code, 204)

    # --- instruments
    def test_instruments_list_and_detail(self):
        self.assertEqual(self.client.get("/trades/instruments/").status_code, 200)
        self.assertEqual(self.client.get("/trades/instruments/AAPL/").json()["name"], "Apple")
        self.assertEqual(self.client.get("/trades/instruments/NOPE/").status_code, 404)

    def test_cannot_delete_instrument_with_trades(self):
        # on_delete=PROTECT: should be refused, not crash with a 500
        r = self.client.delete("/trades/instruments/AAPL/")
        self.assertIn(r.status_code, (400, 403, 409))
