from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    list_filter = ('username', 'first_name', 'last_name', 'email',)
    list_editable = ('is_active',)
    list_display_links = None


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)
    list_display_links = None


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
