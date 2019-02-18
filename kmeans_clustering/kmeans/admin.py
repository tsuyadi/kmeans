from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db.models import Sum, Count

from .models import *

admin.site.site_header = 'Clustering KMEANS'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['cif', 'name', 'birth_date', 'account_no', 'card_no']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account_no', 'channel', 'transaction_type', 'amount', 'transaction_date']
    list_filter = ['channel', 'transaction_type']


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(TransactionSummary)
class TransactionSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'transaction_summary.html'

    list_filter = ('channel__name',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_amount': Sum('amount'),
        }

        response.context_data['summary'] = list(
            qs
            .values('channel__name')
            .annotate(**metrics)
            .order_by('-total_amount')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response


# Register your models here.
# admin.site.register(Customer, CustomerAdmin)
# admin.site.register(TransactionType, TransactionTypeAdmin)
# admin.site.register(Channel, ChannelAdmin)
# admin.site.register(Transaction, TransactionAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
