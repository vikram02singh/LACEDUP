from django.urls import path,include
from .views import  payment_success,checkout 
from . import views


urlpatterns = [
    path('',views.index, name="index"),
    path('contact/',views.contact, name="contact"),
    path('about/',views.about, name="about"),
    path('profile/',views.profile, name="profile"),
    path('privacy/',views.privacy, name="privacy"),
    path('terms/',views.terms, name="terms"),
    path('signin/',views.signin, name="Signin"),
    path('blog/',views.blog, name="blog"),
    path('my_order/',views.my_order, name="order"),
    path('checkout/',views.checkout, name="checkout"),
    path("payment-success/", payment_success, name="payment_success"),
]


