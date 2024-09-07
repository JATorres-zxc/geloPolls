from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
import json


from .serializer import QuestionSerializer
from .models import Choice, Question


class IndexView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generics.RetrieveAPIView):
    queryset = Question.objects.filter(pub_date__lte=timezone.now())
    serializer_class = QuestionSerializer

class ResultsView(generics.RetrieveAPIView):
    queryset = Question.objects.filter(pub_date__lte=timezone.now())
    serializer_class = QuestionSerializer

@csrf_exempt # im having a problem with csrf so i use this to temporarily solve it
def vote(request, question_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_choice_id = data.get('choice')
            
            question = get_object_or_404(Question, pk=question_id)

            selected_choice = question.choices.get(pk=selected_choice_id)
        except (KeyError, Choice.DoesNotExist):
            return JsonResponse({
                'error': "You didn't select a valid choice."
            }, status=400)
        else:
            selected_choice.votes += 1
            selected_choice.save()

            return JsonResponse({
                'message': 'Vote successfully recorded.',
                'question_id': question.id,
                'choice_id': selected_choice.id,
                'votes': selected_choice.votes
            }, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
