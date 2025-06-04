from django.urls import path
from authcart import views

urlpatterns = [ 
    # path('',views.index, name="index"),
    path('signup/',views.signup, name="signup"),
    path('login/',views.handle_login, name="login"),
    path('logout/',views.handle_logout, name="logout"),
    # path('login/', views.login_view, name='login')
]
