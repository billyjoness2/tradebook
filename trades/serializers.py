from rest_framework import serializers
from .models import Instrument, Trade


def validate_positive(value):
    if value <= 0:
        raise serializers.ValidationError("Value must be positive")
    return value


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ["id", "ticker", "name", "asset_class"]


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ["id", "instrument", "side", "quantity", "price", "executed_at"]
        extra_kwargs = {
            "quantity": {"validators": [validate_positive]},
            "price": {"validators": [validate_positive]},
        }






