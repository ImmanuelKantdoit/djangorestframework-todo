from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from todos.models import Todo
from authentication.models import User

class TodoAPITestCase(APITestCase):

    def create_todo(self, user):
        sample_todo = {'title': "Hello", 'desc': "Test"}
        response = self.client.post(reverse('todos'), sample_todo, format='json')
        return response
    
    def authenticate(self):
        user = User.objects.create_user(username="miggy", email="miggy@gmail.com", password="password")
        return user

class TestListCreateTodos(TodoAPITestCase):
   
    def test_should_create_todo(self):
        user = self.authenticate()
        self.client.force_authenticate(user=user)
        previous_todo_count = Todo.objects.all().count()
        response = self.create_todo(user)
        self.assertEqual(Todo.objects.all().count(), previous_todo_count + 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Hello')
        self.assertEqual(response.data['desc'], 'Test')

    def test_should_not_create_todo_with_no_auth(self):
        response = self.create_todo(None)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieves_all_todos(self):
        user = self.authenticate()
        self.client.force_authenticate(user=user)

        # Create a TODO item for the authenticated user
        self.create_todo(user)

        response = self.client.get(reverse('todos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        # Expect the response data to be a dictionary with specific keys
        self.assertIsInstance(response.data, dict)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

        # Now you can check the count and results
        count = response.data['count']
        results = response.data['results']
    
        # Assert that the count is 1 (since you created one TODO item)
        self.assertEqual(count, 1)

        # Assert that results is a list
        self.assertIsInstance(results, list)

    class TestTodoDetailAPIView(TodoAPITestCase):
    
        def test_retrieves_one_item(self):
            user = self.authenticate()
            self.client.force_authenticate(user=user)
            response = self.create_todo(user)

            res = self.client.get(reverse("todo", kwargs={'id' : response.data['id']}))
        
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data['id'], response.data['id'])  # Ensure 'id' is present

            todo = Todo.objects.get(id=response.data['id'])
            self.assertEqual(todo.title, res.data['title'])

        def test_updates_one_item(self):
            user = self.authenticate()
            self.client.force_authenticate(user=user)
    
            # Create a new todo item and get its ID
            response = self.create_todo(user)
            todo_id = response.data['id']
    
            # Attempt to update the created todo
            res = self.client.patch(
                reverse("todo", kwargs={'id': todo_id}), {
                    'title': "New one",
                    'is_complete': True
                })
    
            self.assertEqual(res.status_code, status.HTTP_200_OK)

            updated_todo = Todo.objects.get(id=todo_id)

            self.assertEqual(updated_todo.is_complete, True)
            self.assertEqual(updated_todo.title, 'New one')

        def test_deletes_one_item(self):
            user = self.authenticate()
            self.client.force_authenticate(user=user)
            res = self.create_todo(user)
            prev_db_count = Todo.objects.all().count()

            self.assertGreater(prev_db_count, 0)
            self.assertEqual(prev_db_count, 1)
        
            response = self.client.delete(reverse('todo', kwargs={'id': res.data['id']}))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            # Verify that the item was deleted
            self.assertEqual(Todo.objects.all().count(), 0)
