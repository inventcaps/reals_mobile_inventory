from django.contrib import admin
from .models import (
    Products, ProductTypes, ProductVariants, ProductInventory, ProductBatches, ProductRecipes,
    RawMaterials, RawMaterialInventory, RawMaterialBatches,
    Sales, Expenses, Withdrawals, StockChanges,
    Sizes, SizeUnits, UnitPrices, SrpPrices,
    HistoryLog, HistoryLogTypes, Notifications
)

# Register your models here.

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_type', 'variant', 'size', 'size_unit', 'unit_price', 'srp_price', 'date_created')
    list_filter = ('product_type', 'variant', 'date_created')
    search_fields = ('product_type__name', 'variant__name', 'description')


@admin.register(ProductTypes)
class ProductTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by_admin')
    search_fields = ('name',)


@admin.register(ProductVariants)
class ProductVariantsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by_admin')
    search_fields = ('name',)


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'total_stock', 'restock_threshold')
    list_filter = ('total_stock', 'restock_threshold')


@admin.register(ProductBatches)
class ProductBatchesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'batch_date', 'manufactured_date', 'expiration_date')
    list_filter = ('batch_date', 'expiration_date')
    search_fields = ('product__product_type__name',)


@admin.register(RawMaterials)
class RawMaterialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size', 'unit', 'price_per_unit', 'created_by_admin')
    search_fields = ('name',)
    list_filter = ('unit',)


@admin.register(RawMaterialInventory)
class RawMaterialInventoryAdmin(admin.ModelAdmin):
    list_display = ('material', 'total_stock', 'reorder_threshold')
    list_filter = ('total_stock', 'reorder_threshold')


@admin.register(RawMaterialBatches)
class RawMaterialBatchesAdmin(admin.ModelAdmin):
    list_display = ('id', 'material', 'quantity', 'batch_date', 'received_date', 'expiration_date')
    list_filter = ('batch_date', 'expiration_date')


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'amount', 'date', 'created_by_admin')
    list_filter = ('category', 'date')
    search_fields = ('category', 'description')


@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'amount', 'date', 'created_by_admin')
    list_filter = ('category', 'date')
    search_fields = ('category', 'description')


@admin.register(Withdrawals)
class WithdrawalsAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_type', 'item_id', 'quantity', 'reason', 'date')
    list_filter = ('item_type', 'reason', 'date')


@admin.register(StockChanges)
class StockChangesAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_type', 'item_id', 'quantity_change', 'category', 'date')
    list_filter = ('item_type', 'category', 'date')


@admin.register(Sizes)
class SizesAdmin(admin.ModelAdmin):
    list_display = ('id', 'size_label', 'created_by_admin')
    search_fields = ('size_label',)


@admin.register(SizeUnits)
class SizeUnitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_name', 'created_by_admin')
    search_fields = ('unit_name',)


@admin.register(UnitPrices)
class UnitPricesAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_price', 'created_by_admin')


@admin.register(SrpPrices)
class SrpPricesAdmin(admin.ModelAdmin):
    list_display = ('id', 'srp_price', 'created_by_admin')


@admin.register(HistoryLog)
class HistoryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'log_type', 'log_date')
    list_filter = ('log_type', 'log_date')


@admin.register(HistoryLogTypes)
class HistoryLogTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'created_by_admin')
    search_fields = ('category',)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_type', 'item_id', 'notification_type', 'notification_timestamp', 'is_read')
    list_filter = ('item_type', 'notification_type', 'is_read', 'notification_timestamp')
