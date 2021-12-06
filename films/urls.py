from django.urls import path
from films import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("films/", views.FilmList.as_view(), name="films"),
]

htmx_urlpatterns = [
    path('check_username/', views.check_username, name='check-username'),
    path("films/add/",views.add_films,name="add-film"),
    path("films/delete/<int:pk>/",views.delete_films,name="delete-film"),
    path("films/search/",views.search_film,name="search-film"),
    path("clear-message", views.clear,name="clear"),
    path("sort",views.sort,name="sort"),
    path('detail/<int:pk>', views.detail,name='detail'),
    path('film/upload_photo/<int:pk>', views.upload_photo,name="upload_photo"),
]

urlpatterns += htmx_urlpatterns