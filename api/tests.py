from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
client = APIClient()
class LOGIN_REGISTRATIONTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login_obtaining_token')
        self.token_refresh_url = reverse("token_refresh")

    def test_register_user(self):
        # Test register endpoint
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print()
        print ("Registeration : PASSED")
        

    def test_login_user(self):
        # Create a test user
        User.objects.create_user(username='testuser', password='testpassword')

        # Test login endpoint
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        print()
        print("Login : PASSED")
        


class TOKENTestCase(TestCase):
    def setUp(self):  
        #URLs
        client = APIClient()
        self.home_url = reverse("task-list-create")
        self.login_url = reverse('login_obtaining_token')
        self.register_url = reverse('register')
        self.token_refresh_url = reverse("token_refresh")
        
        
        login_details= {'username': 'testuser', 'password': 'testpassword'}
        #Registering
        client.post(self.register_url, login_details)
        #Logging in
        response = client.post(self.login_url, login_details)
        #Storing token
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    
    
    def test_token_refresh(self):
        data = {"refresh":f"{self.refresh_token}"}
        response = client.post(self.token_refresh_url, data)
        access_token_resp = response.data["access"]
        self.access_token = access_token_resp
        
        self.assertIn("access", response.data)
        print()
        print("Token Refresh: PASSED!")
        



    def test_authenticate_user(self):
        headers = {"Authorization":f"Bearer {self.access_token}"}
        response = client.get(self.home_url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print()
        print("Authentication: PASSED!")
        
        

class APITestCase(TestCase):
    def setUp(self):
        client = APIClient()
        self.home_url = reverse("task-list-create")
        self.login_url = reverse('login_obtaining_token')
        self.register_url = reverse('register')
        
        details= {'username': 'testuser', 'password': 'testpassword'}
        #Registering
        client.post(self.register_url, details)
        #Logging in
        response = client.post(self.login_url, details)
        self.access_token = response.data["access"] 

        #Auth headers
        headers = {"Authorization":f"Bearer {self.access_token}"}


    def test_task_creation(self, *internal:bool):

        data = {"task":"Test", "description":" My API software needs to be tested before publishing"}
        response = client.post(self.home_url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        if internal:
            response = client.get(self.home_url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")#get homepage!
            return response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print()
        print("Task Creation: PASSED!")

    def test_task_list(self):
        response = self.test_task_creation(True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print()
        print("Getting Page: COMPLETED!")
        
    def test_task_retrieval(self):
        task_response = self.test_task_creation(True)
        taskID = task_response.data[0]["uuid"]
        response = client.get(f"/task/{taskID}/", HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.data["uuid"], taskID)
        print()
        print("Getting Task: COMPLETED!")
    
    def test_task_update(self):
        data = {"task":"Testing"}
        taskID = self.test_task_creation(True).data[0]["uuid"]
        response = client.put(f"/task/{taskID}/",data = data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.data["task"], "Testing")
        print()
        print("Task Update: COMPLETED!")
    
    def test_task_deletion(self):
        taskID = self.test_task_creation(True).data[0]["uuid"]
        response = client.delete(f"/task/{taskID}/", HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print()
        print("Task Deletion: COMPLETED!")



