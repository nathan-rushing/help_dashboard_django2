from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Task, TaskWriter, MajorDocu, Writers, Version

admin.site.register(Writers)
admin.site.register(Task)
admin.site.register(TaskWriter)
admin.site.register(MajorDocu)
admin.site.register(Version)
