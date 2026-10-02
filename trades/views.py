from django.shortcuts import render
from .models import Trade, Instrument
from .serializers import TradeSerializer, InstrumentSerializer
from rest_framework import generics

class TradeList(generics.ListCreateAPIView):
    queryset = Trade.objects.all()
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


