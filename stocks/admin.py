from django.contrib import admin
from stocks.models import Stockcode
from stocks.models import BK
from stocks.models import ZXG


# Register your models here.
admin.site.register(Stockcode)
admin.site.register(BK)
admin.site.register(ZXG)
