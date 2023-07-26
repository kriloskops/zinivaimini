from django.contrib import admin

# Register your models here.
from .models import Player, Question, Reply

admin.site.register(Player) 
#admin.site.register(Question) 
admin.site.register(Reply) 


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', "day", "order_num")
    ordering = ("-day", "-order_num")