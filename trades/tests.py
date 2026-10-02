# trades/tests.py
from django.test import TestCase
from .models import Instrument
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
