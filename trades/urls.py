from django.contrib import admin
from django.urls import path, include
from .views import TradeList, InstrumentList, RetrieveInstrument, RetrieveTrade


urlpatterns = [
    path('', TradeList.as_view()),
    path('<int:id>/', RetrieveTrade.as_view()),
    path('instruments/', InstrumentList.as_view()),
    path('instruments/<str:ticker>/', RetrieveInstrument.as_view())
]
