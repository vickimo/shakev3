from django.contrib import admin
from termsheetrater.models import TermFields, TermChoices

class ChoiceInline(admin.StackedInline):
    model= TermChoices
    extra= 3

class PollAdmin(admin.ModelAdmin):
    fieldsets= (
                (None, {'fields': ['term']}),
                ('Weights', {'fields': ['weight'], 'classes': ['collapse']}),
                )
    
    inlines= [ChoiceInline]

admin.site.register(TermFields, PollAdmin)
