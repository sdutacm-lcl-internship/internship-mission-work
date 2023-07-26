"""
URL configuration for xuan81400 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from query.views import query_handles, query_getUserRatings, query_handles1, ask, clearCache, ask_mul, page_not_found, page_not_found_500, page_not_found_503, user_query, get_userInfo

handler404 = page_not_found
handler500 = page_not_found_500
handler503 = page_not_found_503
urlpatterns = [
    path("admin/", admin.site.urls),
    path('clearCache', clearCache),
    #path('', query_handles),
    #handler500 = 'your_app.views.server_error'
    #path('batchGetUserInfo/', query_batchGetUserInfo),
    # path('getUserRatings', query_getUserRatings),
    # path('batchGetUserInfo', query_handles1),
    path('getUserRatings', ask),
    path('batchGetUserInfo', ask_mul),
    path('', user_query),
    path('userInfo', get_userInfo)
]