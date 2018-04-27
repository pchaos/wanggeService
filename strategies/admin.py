from django.contrib import admin
from .models import Strategy
from .models import StrategyType
from .models import StrategyDetail

admin.site.register(StrategyType)
admin.site.register(Strategy)
admin.site.register(StrategyDetail)
