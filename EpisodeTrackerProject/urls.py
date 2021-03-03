"""EpisodeTrackerProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from EpisodeTracker import views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.homeview, name='home'),
    
    path('about/', views.aboutview, name='about'),
    path('report/', views.reportview, name='report'),
    path('profile/', views.profileview, name='profile'),
    path('signup/', views.signupview, name='signup'),
    path('notfound/', views.notfoundview, name='notfound'),
    path('login/', auth_views.LoginView.as_view(), {'template_name': 'login.html'}, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), {'template_name': 'logout.html'}, name='logout'),
    path('profile/pwd/', views.changepwd, name='changepwd'),
    
    path('', include('django.contrib.auth.urls')),
    path('', include('social_django.urls', namespace='social')),

    re_path(r'^series/$', views.seriesview, name='series'),
    path('series/list', views.serieslistview, name='serieslist'),
    path('series/simple', views.seriessimpleview, name='seriessimple'),
    path('series/<slug:slug>', views.seriespage, name = 'seriespage'),
    path('series/edit/<slug:slug>', views.editseriesview, name='editseries'),
    path('series/<slug:series_slug>/<slug:season_slug>', views.seasonspage, name = 'seasonspage'),
    path('series/<slug:series_slug>/<slug:season_slug>/progress', views.seasons_progress_page, name = 'seasons_progress_page'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)