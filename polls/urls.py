from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='question-list-api'),
    path('<int:pk>/', DetailView.as_view(), name='question-detail-api'),
    path('<int:pk>/results/', ResultsView.as_view(), name='question-results-api'),
    path('<int:question_id>/vote/', vote, name='vote-api'),
]