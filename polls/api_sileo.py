from .models import Question, Choice
from django.views import View

from sileo.resource import Resource
from sileo.registration import register
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import json


class ChoiceResource(Resource):
    query_set = Choice.objects.all()
    fields = ['id', 'choice_text', 'votes']
    allowed_methods = ['get_pk', 'filter', 'create', 'update', 'delete']
    filter_fields = ('choice_text__icontains',)

    # Handling the create method for Choice
    def create(self, **kwargs):
        """
        Handle creating a new Choice for a specific question.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Get the choice_text from the data
        choice_text = data.get('choice_text', '')
        # Hardcoded for testing purposes
        # question_id = data.get('question_id', 5)  # Use 5 as default for testing
        # Dynamic retrieval of question_id from data
        question_id = data.get('question_id', None)
        
        # Ensure the choice_text is provided
        if not choice_text:
            return {
                'status_code': 400,
                'error': 'Choice text is required.'
            }

        # Ensure the question exists
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return {
                'status_code': 400,
                'error': 'Question not found.'
            }

        # Create the Choice object
        choice = Choice.objects.create(
            question=question,
            choice_text=choice_text
        )

        # Return a serialized response
        return {
            'status_code': 201,
            'data': self.serialize_choice(choice),
            'message': 'Choice created successfully for the question.'
        }

    # Handling the update method for Choice
    def update(self, **kwargs):
        """
        Handle updating an existing Choice object.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Hardcoded for testing purposes
        # choice_id = data.get('pk', 7)  # Hardcoding pk=7 for testing purposes
        # Dynamic retrieval of choice_id from data
        choice_id = data.get('pk', None)
        
        # Get the new choice_text from the data
        choice_text = data.get('choice_text', '')

        # Ensure choice_text is provided
        if not choice_text:
            return {
                'status_code': 400,
                'error': 'Choice text is required.'
            }

        # Attempt to retrieve the Choice object
        choice = get_object_or_404(Choice, pk=choice_id)

        # Update the choice's text and save it
        choice.choice_text = choice_text
        choice.save()

        # Return a serialized response with the updated choice
        return {
            'status_code': 200,
            'data': self.serialize_choice(choice),
            'message': 'Choice updated successfully.'
        }

    # Handling the delete method for Choice
    def delete(self, **kwargs):
        """
        Handle deleting a specific Choice object.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Hardcoded for testing purposes
        # choice_id = data.get('pk', 7)  # Hardcoded for testing
        # Dynamic retrieval of choice_id from data
        choice_id = data.get('pk', None)

        # Attempt to retrieve the Choice object
        choice = get_object_or_404(Choice, pk=choice_id)

        # Delete the choice
        choice.delete()

        return {
            'status_code': 200,
            'message': 'Choice deleted successfully!'
        }

    def serialize(self, obj):
        """
        Serialize a Question object into a dictionary.
        """
        return {
            'id': obj.id,
            'question_text': obj.question_text,
            'pub_date': obj.pub_date.isoformat(),  # Format date as ISO string
            'choices': [self.serialize_choice(choice) for choice in obj.choices.all()]
        }

    def serialize_choice(self, choice):
        """
        Serialize a Choice object into a dictionary.
        """
        return {
            'id': choice.id,
            'choice_text': choice.choice_text,
            'votes': choice.votes,
        }

    def get_pk(self, **kwargs):
        """
        If 'id' is provided, return the result view of that specific question.
        Otherwise, return an error or empty response.
        """
        # print("KWARGS:", kwargs)
        question_id = kwargs.get('pk', None)

        if question_id:
            # Return the result view of a single question, return (question and votes)
            choice = get_object_or_404(Choice, pk=question_id)
            serialized_data = self.serialize_choice(choice)
            return {
                'status_code': 200,
                'data': serialized_data
            }

        return {
            'status_code': 404,
            'error': 'Question not found'
        }



class QuestionResource(Resource):
    query_set = Question.objects.all()
    fields = ['id', 'question_text', 'pub_date']
    related_fields = {
        'choices': ChoiceResource
    }
    allowed_methods = ['get_pk', 'filter', 'create', 'update', 'delete']
    filter_fields = ('question_text__icontains',)

    # Handling the create method for Question
    def create(self, **kwargs):
        """
        Handle creating a new Question object.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Get the question_text from the request body
        question_text = data.get('question_text', '')

        # Validate the question_text input
        if not question_text:
            return {
                'status_code': 400,
                'error': 'Question text is required.'
            }

        # Create the Question object
        question = Question.objects.create(
            question_text=question_text,
            pub_date=timezone.now(),  # Use the current timestamp as the publication date
        )

        # Return a serialized response
        return {
            'status_code': 201,
            'data': self.serialize(question),
            'message': 'Question created successfully.'
        }

    # Handling the update method for Question
    def update(self, **kwargs):
        """
        Update a Question's question_text.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Get the question ID from the data
        # question_id = data.get('pk', 5)  # Hardcoded pk=5 for testing
        # Dynamic retrieval of question_id from data
        question_id = data.get('pk', None)

        # Ensure the question ID is provided
        if not question_id:
            return {
                'status_code': 400,
                'error': 'Question ID is required.'
            }

        # Attempt to retrieve the question
        question = get_object_or_404(Question, pk=question_id)

        # Get the new question text from the data
        question_text = data.get('question_text', '')

        # Ensure question_text is provided
        if not question_text:
            return {
                'status_code': 400,
                'error': 'Question text is required.'
            }

        # Update the question's question_text and save it
        question.question_text = question_text
        question.save()

        # Return the serialized updated question
        return {
            'status_code': 200,
            'data': self.serialize(question),
            'message': 'Question updated successfully.'
        }

    # Handling the delete method for Question
    def delete(self, **kwargs):
        """
        Handle deleting a specific Question object.
        """
        try:
            # Extract the data from the request body
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        # Get the question ID from the data
        # question_id = data.get('pk', 5)  # Hardcoded pk=5 for testing
        # Dynamic retrieval of question_id from data
        question_id = data.get('pk', None)

        # Ensure the question ID is provided
        if not question_id:
            return {
                'status_code': 400,
                'error': 'Question ID is required.'
            }

        # Attempt to retrieve the question
        question = get_object_or_404(Question, pk=question_id)

        # Delete the question
        question.delete()

        return {
            'status_code': 200,
            'message': 'Question deleted successfully!'
        }

    # Handling custom logic for voting
    def vote(self, data, **kwargs):
        """
        Handles voting for a specific choice.
        """
        question_id = data.get('question_id')
        selected_choice_id = data.get('choice')

        question = get_object_or_404(Question, pk=question_id)
        try:
            selected_choice = question.choices.get(pk=selected_choice_id)
        except Choice.DoesNotExist:
            return {
                'status_code': 400,
                'error': "You didn't select a valid choice."
            }

        selected_choice.votes += 1
        selected_choice.save()

        return {
            'status_code': 200,
            'message': 'Vote successfully recorded.',
            'question_id': question.id,
            'choice_id': selected_choice.id,
            'votes': selected_choice.votes
        }

    # Handling minus vote
    def minus_vote(self, data, **kwargs):
        """
        Handle decreasing the votes for a specific choice.
        """
        choice_id = data.get('choice_id')
        choice = get_object_or_404(Choice, pk=choice_id)

        if choice.votes > 0:
            choice.votes -= 1
            choice.save()
            return {
                'status_code': 200,
                'message': 'Vote decremented successfully!',
                'votes': choice.votes
            }
        else:
            return {
                'status_code': 400,
                'message': 'Votes cannot be negative.'
            }

    # Serialize Question
    def serialize(self, obj):
        """
        Serialize a Question object into a dictionary.
        """
        return {
            'id': obj.id,
            'question_text': obj.question_text,
            'pub_date': obj.pub_date.isoformat(),  # Format date as ISO string
            'choices': [self.serialize_choice(choice) for choice in obj.choices.all()]
        }

    def serialize_choice(self, choice):
        """
        Serialize a Choice object into a dictionary.
        """
        return {
            'id': choice.id,
            'choice_text': choice.choice_text,
            'votes': choice.votes,
        }

    # Filter method to get the last five published questions, excluding future ones
    def filter(self, **kwargs):
        """
        Return the last five published questions (excluding future questions)
        in a serialized format.
        """
        queryset = Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

        # Serialize the queryset into a list of dictionaries
        serialized_data = [self.serialize(question) for question in queryset]

        return {
            'status_code': 200,
            'data': serialized_data
        }

    # Handling get_pk for returning question details
    def get_pk(self, **kwargs):
        """
        If 'id' is provided, return the detail view of that specific question.
        Otherwise, return an error or empty response.
        """
        # question_id = kwargs.get('pk', 5)  # Hardcoded pk=5 for testing
        # Dynamic retrieval of question_id from kwargs
        question_id = kwargs.get('pk', None)

        if question_id:
            # Return the detail view of a single question
            question = get_object_or_404(Question, pk=question_id, pub_date__lte=timezone.now())
            serialized_data = self.serialize(question)
            return {
                'status_code': 200,
                'data': serialized_data
            }

        return {
            'status_code': 404,
            'error': 'Question not found'
        }
  
        
class VotingResource(Resource):
    query_set = Choice.objects.all()
    fields = ['id', 'choice_text', 'votes']
    allowed_methods = ['create']

    def serialize(self, choice):
        """
        Serialize a Choice object into a dictionary.
        """
        return {
            'id': choice.id,
            'choice_text': choice.choice_text,
            'votes': choice.votes,
        }

    def create(self, **kwargs):
        """
        Handle voting for a specific choice (incrementing the vote count).
        """
        try:
            # Extract data from the request body (POST request)
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            return {
                'status_code': 400,
                'error': 'Invalid JSON format.'
            }

        choice_id = data.get('choice_id', None)

        # Ensure choice_id is provided
        if not choice_id:
            return {
                'status_code': 400,
                'error': 'Choice ID is required.'
            }

        # Attempt to get the Choice object
        try:
            choice = Choice.objects.get(pk=choice_id)
        except Choice.DoesNotExist:
            return {
                'status_code': 400,
                'error': 'Choice not found.'
            }

        # Increment the vote count
        choice.votes += 1
        choice.save()

        # Serialize the updated choice object
        serialized_data = self.serialize(choice)

        return {
            'status_code': 200,
            'data': serialized_data,
            'message': 'Vote successfully recorded.'
        }


# Register the resources to make them available via HTTP requests
register(namespace='vote', name='vote', resource=VotingResource, version='v1')
register(namespace='choice', name='choice', resource=ChoiceResource, version='v1')
register(namespace='question', name='question', resource=QuestionResource, version='v1')











