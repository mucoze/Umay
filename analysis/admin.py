from django.contrib import admin
from analysis.models import Analysis


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['id']

    class Meta:
        model = Analysis


admin.site.register(Analysis, AnalysisAdmin)

