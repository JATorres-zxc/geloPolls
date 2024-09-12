from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='question-list-api'),
    path('<int:pk>/', DetailView.as_view(), name='question-detail-api'),
    path('<int:pk>/results/', ResultsView.as_view(), name='question-results-api'),
    path('<int:question_id>/vote/', vote, name='vote-api'),
    path('create/', create_question, name='create_question'),
    path('<int:question_id>/edit/', edit_question, name='edit_question'), 
    path('<int:question_id>/delete/', delete_question, name='delete_question'), 
    path('<int:question_id>/add_choice/', add_choice, name='add_choice'),
    path('choice/<int:choice_id>/edit/', edit_choice, name='edit_choice'),
    path('choice/<int:choice_id>/delete/', delete_choice, name='delete_choice'),
    path('choice/<int:choice_id>/minus_vote/', minus_vote, name='minus_vote'), 
  
]