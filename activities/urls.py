from django.urls import path
from .views import home,select_child,add_child,logout_view,select_activity,delete_child, start_activity, stop_activity, child_report, activity_report
urlpatterns = [
    path('home/', home, name='homepage'),
    path("selectchild/",select_child, name='selectchild'),
    path("addchild/",add_child, name='addchild'),
    path('logout/', logout_view, name='logout'),
    path('selectactivity/<int:child_id>/', select_activity, name='selectactivity'),
    path('start-activity/<int:child_id>/<int:activity_id>/', start_activity, name='start_activity'),
    path('stop-activity/<int:child_id>/<int:activity_id>/', stop_activity, name='stop_activity'),
    path('child-report/<int:child_id>/', child_report, name='child_report'), 
    path('activity-report/<int:child_id>/<int:activity_id>/', activity_report, name='activity_report'),
    path('selectchild/<int:child_id>/delete/', delete_child, name='delete_child'),
]