
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile',views.profile,name='profile'),
    path('profile/<str:user>',views.profile,name='profile'),
    path('profile/<str:user>/followers',views.followers,name='followers'),
    path('profile/<str:user>/followed',views.followed,name='followed'),
    path('following',views.following,name='following'),
    #API
    ##API for creating a new post
    path('create',views.create,name='create'),
    ##API for list of posts based on query
    path('posts',views.posts,name='posts'),
    ##API for like
    path('like',views.like,name='like')
]
