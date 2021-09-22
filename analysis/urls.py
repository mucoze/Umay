from django.urls import path
from .views import *

app_name = 'analysis'

urlpatterns = [
    path('index/', analysis_index, name='index'),
    path('', analysis_create, name='create'),
    path('detail/<int:id>', analysis_detail, name='detail'),
    path('index/detail/<int:id>', analysis_detail, name='detail2'),
]

