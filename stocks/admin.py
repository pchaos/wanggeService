from django.contrib import admin
from stocks.models import Listing
from stocks.models import BlockDetail, Block
from stocks.models import RPS, RPSprepare
from stocks.models import HSGTCGHold, HSGTCGHold

# Register your models here.
admin.site.register(Listing)
admin.site.register(Block)
admin.site.register(BlockDetail)
admin.site.register(RPS)
admin.site.register(RPSprepare)


from mptt.admin import MPTTModelAdmin

from .models import Category, Product

# Register your models here.
class CategoryAdmin(MPTTModelAdmin):
    fields = ['name', 'description', 'parent']
    list_display = ('name', )

    mptt_level_indent = 15

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    ordering = ('code',)
    fieldsets = [
        (None, {'fields': ['code', 'stocks', 'category']}),
        (None, {'fields': ['name', 'description',]}),
        ('价格', {'fields': ['priceAustria'], 'classes': ['grp-collapse  grp-closed']}),
    ]
    # change_list_template = 'admin/product_change_list.html'
    list_display = ('code', 'name', 'category')
    search_fields = ['code']

    list_filter = ('name',)


admin.site.register(Product, ProductAdmin)