from django.contrib import admin
from .models import Instrument, Trade

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ["ticker", "name", "asset_class"]

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ["instrument", "side", "quantity", "price", "executed_at"]
    list_filter = ["side", "instrument"]