from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='question-list-api'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]