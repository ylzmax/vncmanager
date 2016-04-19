from django.contrib import admin
from vnc.models import *

# Register your models here.
class serveradmin(admin.ModelAdmin):
	list_filter=("servername","serverip")
	list_display=("servername","serverip")
	


admin.site.register(server,serveradmin)
admin.site.register(vncserver)
