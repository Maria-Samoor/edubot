from django.urls import path
from .views import home,select_child,add_child,logout_view,select_activity,delete_child
urlpatterns = [
    path('home/', home, name='homepage'),
    path("selectchild/",select_child, name='selectchild'),
    path("addchild/",add_child, name='addchild'),
    path('logout/', logout_view, name='logout'),
    path('selectactivity/', select_activity, name='selectactivity'),
    path('selectchild/<int:child_id>/delete/', delete_child, name='delete_child'),
]