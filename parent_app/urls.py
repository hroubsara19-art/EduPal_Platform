from django.urls import path
from . import views

app_name = 'parent'

urlpatterns = [
    path('dashboard/parent/', views.parent_portal, name='parent_portal'),
    path('parent/reports/', views.reports_dashboard, name='reports_dashboard'),
    path('parent/child-report/', views.child_report, name='child_report'),
    path('parent/session/<int:session_id>/', views.session_details, name='session_details'),
    path('parent/profile/',   views.parent_profile, name='profile'),
]