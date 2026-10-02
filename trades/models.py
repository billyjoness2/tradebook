from django.db import models

class Instrument(models.Model):

    class AssetClass(models.TextChoices):
        EQUITY = "EQUITY", "Equity"    
        FX = "FX", "FX"
        CRYPTO = "CRYPTO", "Crypto"
        DEBT =  "DEBT", "Debt"

    ticker = models.CharField(max_length = 10, unique = True)
    name = models.CharField(max_length = 100)
    asset_class = models.CharField(max_length=10, choices = AssetClass.choices)

    def __str__(self):
        return self.ticker


class Trade(models.Model):

    class Side(models.TextChoices):
            BUY = "BUY", "Buy"    
            SELL = "SELL", "Sell"

    instrument = models.ForeignKey(Instrument, on_delete = models.PROTECT)
    side = models.CharField(max_length = 10, choices = Side.choices)
    quantity = models.DecimalField(max_digits = 100, decimal_places = 8)
    price = models.DecimalField(max_digits = 100, decimal_places = 6)
    executed_at = models.DateTimeField()

    def __str__(self):
            return f'{self.side} order for {self.quantity} of {self.instrument.ticker} @ {self.price} on {self.executed_at}'



    