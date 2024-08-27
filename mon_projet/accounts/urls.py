from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('generate_pdf/<int:employee_id>/', views.generate_employee_pdf_indiv, name='generate_employee_pdf'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('add_account_type/', views.add_account_type, name='add_account_type'),
    path('employee_form/', views.add_account_type, name='employee_form'),
    path('add_profile/', views.add_profile, name='add_profile'),
    path('add_manager/', views.add_manager, name='add_manager'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('employee/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('employee/<int:pk>/delete/', views.delete_employee, name='delete_employee'),
    path('edit_manager/<int:manager_id>/', views.edit_manager, name='edit_manager'),
    path('delete_manager/<int:manager_id>/', views.delete_manager, name='delete_manager'),
    path('add_department/', views.add_department, name='add_department'),
    path('generate_pdf/<int:employee_id>/', views.generate_pdf, name='generate_pdf'),
    path('get_account_types/', views.get_account_types, name='get_account_types'),
    path('logout/', views.logout_view, name='logout'),
]
