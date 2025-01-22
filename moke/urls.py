from django.conf import settings
from django.conf.urls.static import static  # Import static for serving media files
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('test/', views.test_list, name='test_list'),  # List all tests
    path('test/<int:test_id>/', views.take_test, name='take_test'),  # View and take individual test
    path('test/<int:test_id>/take/', views.take_test, name='take_test'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/completed/', views.test_completed, name='test_completed'), 
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/results/', views.test_completed, name='test_results'),
   
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
