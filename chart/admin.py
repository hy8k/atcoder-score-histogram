from django.contrib import admin

from .models import ContestInfo, ResultInfo, TaskInfo

admin.site.register(ContestInfo)
admin.site.register(TaskInfo)
admin.site.register(ResultInfo)