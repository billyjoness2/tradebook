from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from .models import Trade, Instrument
from .serializers import TradeSerializer, InstrumentSerializer
from rest_framework import generics
from decimal import Decimal, InvalidOperation
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db.models import ProtectedError
from rest_framework import status


RANGE_FIELDS = {
    "quantity": Decimal,
    "price": Decimal,
    "executed_at": parse_datetime
}

class TradeList(generics.ListCreateAPIView):
    queryset = Trade.objects.all()

    def get_queryset(self):
        
        qs = Trade.objects.select_related("instrument")

        params = self.request.query_params
         
        ticker = params.get("ticker")
        if ticker:
            ticker_upper = ticker.upper()
            qs = qs.filter(instrument__ticker = ticker_upper)

        asset_class = params.get("asset_class")
        if asset_class:
            qs = qs.filter(instrument__asset_class = asset_class)

        side = params.get("side")
        if side:
            if side not in ["BUY", "SELL"]:
                raise ValidationError(f"side must be BUY or SELL. got: {side}")
            else:
                qs = qs.filter(side = side)

        for field, parse in RANGE_FIELDS.items():
            for suffix, lookup in (("min", "gte"), ("max", "lte")):
                name = f"{field}_{suffix}"
                raw = params.get(name)
                if raw:
                    try:
                        value = parse(raw)
                    except (InvalidOperation, ValueError):
                        value = None
                    if value is None:
                        raise ValidationError({name: "invalid value"})
                    qs = qs.filter(**{f"{field}__{lookup}": value})

        return qs.order_by("-executed_at")
 
    serializer_class = TradeSerializer

class InstrumentList(generics.ListCreateAPIView):
        queryset = Instrument.objects.all()
        serializer_class = InstrumentSerializer

class RetrieveTrade(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = "id"
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
                             
class RetrieveInstrument(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = "ticker"
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"detail": "cannot delete an instrument that has trades."}, status = status.HTTP_409_CONFLICT)


