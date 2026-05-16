from django.urls import path
from . import views

app_name = 'parent'

urlpatterns = [
    path('dashboard/parent/', views.parent_portal, name='parent_portal'),
    path('parent/profile/',   views.parent_profile, name='profile'),
    
    # ── Notification endpoints (for parent account) ────────────────────
    # Re-route to accounts app notification views
    path('notifications/',                     views.notifications_list,      name='notifications_list'),
    path('notifications/unread/',              views.notifications_unread,    name='notifications_unread'),
    path('notifications/mark-all/',            views.notifications_mark_read, name='notifications_mark_read'),
    path('notifications/mark/<int:notif_id>/', views.notifications_mark_one,  name='notifications_mark_one'),
]