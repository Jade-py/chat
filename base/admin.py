from django.contrib import admin
from .models import Message, UploadedFile, Department, UserProfile, tblusers


admin.site.register(Message)
admin.site.register(UserProfile)
admin.site.register(UploadedFile)
admin.site.register(Department)
admin.site.register(tblusers)
# Register your models here.
