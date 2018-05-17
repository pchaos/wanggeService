from django.contrib import admin
from stocks.models import Listing
from stocks.models import BK
from stocks.models import BKDetail
from stocks.models import RPS, RPSprepare

# Register your models here.
admin.site.register(Listing)
admin.site.register(BK)
admin.site.register(BKDetail)
admin.site.register(RPS)
admin.site.register(RPSprepare)
