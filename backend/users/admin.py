# isort: skip_file
from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('first_name', 'last_name', 'username',)
    list_filter = ('email', 'username', 'role',)
    list_display_links = ('pk', 'username',)
    empty_value_display = '-/-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following', 'sub_id')
    search_fields = ('user', 'following',)
    list_filter = ('user',)

    def sub_id(self, sub):
        return sub.following.id


admin.site.unregister(Group)
