
# Register your models here.

from django.contrib import admin
from .models import Course,Tag,TaskTag,Task,Comment,WeatherCache

admin.site.register(Course)
admin.site.register(Tag)
admin.site.register(TaskTag)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(WeatherCache)
