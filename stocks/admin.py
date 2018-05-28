from django.contrib import admin
from stocks.models import Listing
from stocks.models import BlockDetail, Block
from stocks.models import RPS, RPSprepare

# Register your models here.
admin.site.register(Listing)
admin.site.register(Block)
admin.site.register(BlockDetail)
admin.site.register(RPS)
admin.site.register(RPSprepare)
