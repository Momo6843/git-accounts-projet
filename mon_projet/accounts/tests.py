from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Manager, Employee, Profile, AccountType, Department
from .forms import ManagerForm, EmployeeForm, ProfileForm, AccountTypeForm, DepartmentForm
from django.contrib.messages import get_messages

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='adddd', password='adminpass', email='admin@example.com')
        self.manager_user = User.objects.create_user(username='manager', password='managerpass', email='manager@example.com')
        
        self.account_type = AccountType.objects.create(name='Test Account Type')

        # Créez un profil               
        self.profile = Profile.objects.create(name='Test Profile')

        # Associez le type de compte au profil
        self.profile.account_types.add(self.account_type)
        self.manager = Manager.objects.create(user=self.manager_user)
        self.employee = Employee.objects.create(first_name='John', last_name='Doe', email='john.doe@example.com')

    def test_login_view(self):
    # Test for valid admin login
        response = self.client.post(reverse('login'), {'username': 'adddd', 'password': 'adminpass'})
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Test for valid manager login
        response = self.client.post(reverse('login'), {'username': 'manager', 'password': 'managerpass'})
        self.assertEqual(response.status_code, 302) 
        print("loginnnnn"+ str(response.status_code))
        self.assertRedirects(response, reverse('manager_dashboard'))

        # Test for invalid login credentials
        response = self.client.post(reverse('login'), {'username': 'unknown', 'password': 'password'})
        self.assertEqual(response.status_code, 200)  # Should render the login page
        self.assertContains(response, 'Invalid credentials')




    def test_edit_manager(self):
    # Connecter un utilisateur avec des credentials valides
        self.client.login(username='adddd', password='adminpass')  # Assurez-vous que ces credentials sont corrects
        
        form_data = {
            'username': 'newmanager',
            'password': 'newpass',
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'email': 'updatedemail@example.com'
        }
        response = self.client.post(reverse('edit_manager', args=[self.manager.id]), form_data)
        
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Recharger l'utilisateur depuis la base de données pour vérifier les modifications
        self.manager.user.refresh_from_db()
        self.assertEqual(self.manager.user.username, 'newmanager')
        self.assertTrue(self.manager.user.check_password('newpass'))  # Vérifie que le mot de passe est bien mis à jour
        self.assertEqual(self.manager.user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.manager.user.last_name, 'UpdatedLastName')
        self.assertEqual(self.manager.user.email, 'updatedemail@example.com')


    def test_delete_manager(self):
        self.client.login(username='adddd', password='adminpass')
        response = self.client.post(reverse('delete_manager', args=[self.manager.id]))
        self.assertEqual(response.status_code, 302) 
        print("MANAGER"+str(response.status_code))# Should redirect
        self.assertRedirects(response, reverse('admin_dashboard'))
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(id=self.manager.id)

    def test_edit_employee(self):
        self.client.login(username='manager', password='managerpass')
        form_data = {'first_name': 'Jane', 'last_name': 'Doe', 'email': 'jane.doe@example.com'}
        response = self.client.post(reverse('edit_employee', args=[self.employee.id]), form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('manager_dashboard'))
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.first_name, 'Jane')

    def test_delete_employee(self):
        self.client.login(username='manager', password='managerpass')
        response = self.client.post(reverse('delete_employee', args=[self.employee.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('manager_dashboard'))
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee.id)

    def test_logout_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('login'))

    def test_manager_dashboard(self):
        self.client.login(username='manager', password='managerpass')
        response = self.client.get(reverse('manager_dashboard'))
        print(" managerrrrrrrrrrrrrrrr"+ str(response.status_code))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Manager Dashboard</h1>')

    def test_admin_dashboard(self):
        self.client.login(username='adddd', password='adminpass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        print("addd" +str(response.status_code))
        self.assertContains(response, '<h2>Admin Dashboard</h2>')

    def test_add_account_type(self):
        self.client.login(username='admin', password='adminpass')
        form_data = {'name': 'New Account Type'}
        response = self.client.post(reverse('add_account_type'), form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(AccountType.objects.filter(name='New Account Type').exists())
    
    def test_add_profile(self):
        # Crée une instance du client de test
        client = Client()
        
        # Crée quelques types de comptes pour le test
        account_type1 = AccountType.objects.create(name='Type 1')
        account_type2 = AccountType.objects.create(name='Type 2')
        
        # Crée un utilisateur admin pour se connecter
        admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        
        # Connecte l'utilisateur admin
        client.login(username='admin', password='adminpass')
        
        # Prépare les données du formulaire avec des types de comptes inclus
        form_data = {
            'name': 'New Profile',
            'account_types': [account_type1.id, account_type2.id]  # Inclure les types de comptes
        }
        
        # Soumet les données du formulaire
        response = client.post(reverse('add_profile'), form_data)
        
        # Affiche le code de statut de la réponse
        print("PROFILE" + str(response.status_code))
        
        # Vérifie que la réponse redirige comme prévu
        assert response.status_code == 302  # Doit rediriger
        assert response.url == reverse('admin_dashboard')
        
        # Vérifie que le profil a été créé avec les types de comptes associés
        profile = Profile.objects.get(name='New Profile')
        assert profile.account_types.filter(id=account_type1.id).exists()
        assert profile.account_types.filter(id=account_type2.id).exists()
    def test_add_manager(self):
    # Connexion avec des credentials valides
        self.client.login(username='admin', password='adminpass')  # Assurez-vous que ces credentials sont corrects
        
        form_data = {
            'username': 'newmanager',
            'password': 'newpass',
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'email': 'manager@example.com'
        }
        response = self.client.post(reverse('add_manager'), form_data)
        
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        # Vérifier que le nouvel utilisateur a été créé
        self.assertTrue(User.objects.filter(username='newmanager').exists())
        
        # Optionnel : Vérifier si un Manager associé a été créé (si applicable)
        new_user = User.objects.get(username='newmanager')
        self.assertTrue(Manager.objects.filter(user=new_user).exists())

    def test_add_employee(self):
        self.client.login(username='manager', password='managerpass')
        form_data = {'first_name': 'New', 'last_name': 'Employee', 'email': 'new.employee@example.com'}
        response = self.client.post(reverse('add_employee'), form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect
        print("admin" +str(response.status_code))
        self.assertRedirects(response, reverse('manager_dashboard'))
        self.assertTrue(Employee.objects.filter(email='new.employee@example.com').exists())

    def test_generate_pdf(self):
        self.client.login(username='addd', password='adminpass')
        response = self.client.get(reverse('generate_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_add_department(self):
        self.client.login(username='adddd', password='adminpass')
        form_data = {'name': 'New Department'}
        response = self.client.post(reverse('add_department'), form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect
       
        self.assertRedirects(response, reverse('admin_dashboard'))
    def test_get_account_types_with_profile_id(self):
        url = f'/accounts/get_account_types/?profile_id={self.profile.id}'
        
        # Envoyer une requête GET à la vue avec le profile_id
        response = self.client.get(url)
        
        # Vérifier que la réponse a un code de statut 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse JSON contient les types de comptes associés au profil
        expected_data = {'account_types': [self.account_type.id]}
        self.assertJSONEqual(response.content, expected_data)