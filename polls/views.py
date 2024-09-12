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
    
@csrf_exempt 
def create_question(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_text = data.get('question_text', '')
        if question_text:
            question = Question.objects.create(
                question_text=question_text,
                pub_date=timezone.now(),
            )
            return JsonResponse({
                'id': question.id,
                'question_text': question.question_text,
                'pub_date': question.pub_date,
            })
        return JsonResponse({'error': 'Invalid input'}, status=400)
    
@csrf_exempt    
def edit_question(request, question_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        question_text = data.get('question_text', '')
        
        if question_text:
            question = get_object_or_404(Question, pk=question_id)
            question.question_text = question_text
            question.save()
            return JsonResponse({
                'id': question.id,
                'question_text': question.question_text,
            })
        return JsonResponse({'error': 'Invalid input'}, status=400)
    
@csrf_exempt    
def delete_question(request, question_id):
    if request.method == 'DELETE':
        question = get_object_or_404(Question, pk=question_id)
        question.delete()
        return JsonResponse({'message': 'Question deleted successfully!'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt    
def add_choice(request, question_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        choice_text = data.get('choice_text', '')

        if choice_text:
            question = get_object_or_404(Question, pk=question_id)
            choice = Choice.objects.create(question=question, choice_text=choice_text)
            return JsonResponse({
                'id': choice.id,
                'choice_text': choice.choice_text,
            }, status=201)
        return JsonResponse({'error': 'Invalid input'}, status=400)
    
    
@csrf_exempt    
def edit_choice(request, choice_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        choice_text = data.get('choice_text', '')

        if choice_text:
            choice = get_object_or_404(Choice, pk=choice_id)
            choice.choice_text = choice_text
            choice.save()
            return JsonResponse({
                'id': choice.id,
                'choice_text': choice.choice_text,
            }, status=200)
        return JsonResponse({'error': 'Invalid input'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt    
def delete_choice(request, choice_id):
    if request.method == 'DELETE':
        choice = get_object_or_404(Choice, pk=choice_id)
        choice.delete()
        return JsonResponse({'message': 'Choice deleted successfully!'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def minus_vote(request, choice_id):
    if request.method == 'POST':
        choice = get_object_or_404(Choice, pk=choice_id)

        if choice.votes > 0:
            choice.votes -= 1
            choice.save()
            return JsonResponse({'message': 'Vote decremented successfully!', 'votes': choice.votes}, status=200)
        else:
            return JsonResponse({'message': 'Votes cannot be negative.', 'votes': choice.votes}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)