from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.template.loader import get_template
from django.conf import settings

from .forms import AccountTypeForm, ManagerForm, EmployeeForm, ProfileForm, DepartmentForm
from .models import AccountType, Manager, Employee, Profile, EmployeeAccountType

from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import os
import io
import pandas as pd

from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

@csrf_protect
@login_required
def edit_employee(request, pk):
    try:
        employee = get_object_or_404(Employee, pk=pk)
    except Http404:
        messages.error(request, "This employee does not exist.")
        return redirect('manager_dashboard')  # Redirigez vers une vue appropriée

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('manager_dashboard')
    else:
        form = EmployeeForm(instance=employee)
        
    managers = Manager.objects.all()  # Incluez les managers dans le contexte
    return render(request, 'accounts/add_employee.html', {'form': form, 'managers': managers,'action': 'edit'})

@csrf_protect
@login_required
def generate_employee_pdf_indiv(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    # Préparer les données pour le PDF
    data = {
        'Nom': employee.last_name,
        'Prénom': employee.first_name,
        'Email': employee.email,
        'Département': employee.department.name if employee.department else '',
        'Compte': ', '.join([account.name for account in employee.account_types.all()])
    }

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Créer des styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=22, alignment=1)
    normal_style = ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontSize=14, alignment=0)

    # Créer le titre
    title = Paragraph(f"Rapport de {employee.first_name} {employee.last_name} ({employee_id})", title_style)
    
    # Espacement entre le titre et le contenu
    spacer = Spacer(1, 0.5 * inch)

    # Créer le contenu du PDF
    content = [title, spacer]
    for key, value in data.items():
        content.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
        content.append(Spacer(1, 0.2 * inch))  # Espacement entre les lignes de contenu

    # Ajuster la largeur de la colonne pour occuper toute la largeur de la page
    pdf.build(content)

    # Récupérer le PDF en mémoire
    buffer.seek(0)
    
    # Nom du fichier basé sur le nom et l'ID de l'employé
    filename = f"{employee.first_name}_{employee.last_name}_{employee_id}.pdf"
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_protect
@login_required
def manager_dashboard(request):
    query = request.GET.get('q')
    if query:
        employees = Employee.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(department__name__icontains=query) |
            Q(account_types__name__icontains=query)
        ).distinct()
    else:
        employees = Employee.objects.all()

    # Définir le message à passer au template
    no_results_message = "Aucun utilisateur trouvé" if not employees.exists() else ""
    
    managers = Manager.objects.all()  # Inclure les managers dans le contexte

    return render(request, 'accounts/manager_dashboard.html', {
        'employees': employees,
        'managers': managers,
        'no_results_message': no_results_message  # Passer le message au template
    })
@csrf_protect
@login_required
def generate_pdf(request):
    # Récupérer les données de la base de données
    employees = Employee.objects.prefetch_related('account_types', 'department')

    # Préparer les données pour le DataFrame
    data = []
    for employee in employees:
        account_types = ', '.join([account.name for account in employee.account_types.all()])
        data.append({
            'Nom': employee.last_name,
            'Prenom': employee.first_name,
            'Email': employee.email,
            'Departement': employee.department.name if employee.department else '',
            'Compte': account_types
        })

    df = pd.DataFrame(data)

    # Créer un fichier PDF en mémoire
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Créer des styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Créer le titre
    title = Paragraph("Rapport des Employés avec Départements et Comptes", title_style)

    # Créer le tableau
    table = Table([df.columns.tolist()] + df.values.tolist())
    table.setStyle(table_style)

    # Ajouter le titre et le tableau au document PDF
    elements = [title, table]
    pdf.build(elements)

    # Récupérer le PDF en mémoire et le retourner dans la réponse HTTP
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'manager'):
                return redirect('manager_dashboard')
            else:
                return redirect('manager_dashboard')  # Redirecting to manager_dashboard as default
        else:
            return render(request, 'accounts/login.html', {'error': 'Username or password incorect'})
    return render(request, 'accounts/login.html')
# views.py

@csrf_protect
@login_required
def get_account_types(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    account_types = profile.account_types.values_list('id', flat=True)
    return JsonResponse({'account_types': list(account_types)})

@csrf_protect
@login_required
def is_admin(user):
    return user.is_superuser

@csrf_protect
@login_required
def edit_manager(request, manager_id):
    try:
        manager = get_object_or_404(Manager, id=manager_id)
    except Http404:
        messages.error(request, "This manager does not exist.")
        return redirect('admin_dashboard')  # Redirigez vers une vue appropriée

    if request.method == 'POST':
        form = ManagerForm(request.POST, instance=manager.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manager updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = ManagerForm(instance=manager.user)
        
    return render(request, 'accounts/edit_manager.html', {'form': form, 'manager': manager})


@csrf_protect
@login_required
def delete_manager(request, manager_id):
    manager = get_object_or_404(Manager, id=manager_id)
    
    # Supprimer le manager directement sans confirmation
    manager.user.delete()
    messages.success(request, 'Manager deleted successfully.')
    
    return redirect('admin_dashboard')

@csrf_protect
@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Supprimer l'employé directement sans confirmation
    employee.delete()
    messages.success(request, 'Employee deleted successfully.')
    
    return redirect('manager_dashboard')

@csrf_protect
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_protect
@login_required
def admin_dashboard(request):
    managers = Manager.objects.all()
    return render(request, 'accounts/admin_dashboard.html', {'managers': managers})

@csrf_protect
@login_required
def add_account_type(request):
    if request.method == 'POST':
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = AccountTypeForm()
    managers = Manager.objects.all()  # Include managers in the context
    return render(request, 'accounts/add_account_type.html', {'form': form, 'managers': managers})

@csrf_protect
@login_required
def add_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProfileForm()
    account_types = AccountType.objects.all()
    managers = Manager.objects.all()  # Include managers in the context
    return render(request, 'accounts/add_profile.html', {'form': form, 'account_types': account_types, 'managers': managers})

@csrf_protect
@login_required
def add_manager(request):
    if request.method == 'POST':
        form = ManagerForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create Manager instance for the new user
            Manager.objects.create(user=user)
            messages.success(request, 'Manager added successfully.')
            return redirect('admin_dashboard')
    else:
        form = ManagerForm()
    managers = Manager.objects.all()  # Include managers in the context
    return render(request, 'accounts/add_manager.html', {'form': form, 'managers': managers})

@csrf_protect
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()  # Laisse le formulaire gérer les relations ManyToMany
            return redirect('manager_dashboard')
    else:
        form = EmployeeForm()
    context = {
        'form': form,
        'profiles': Profile.objects.all(),
        'account_types': AccountType.objects.all(),
        'action': 'add'
    }
    return render(request, 'accounts/add_employee.html', context)
@csrf_protect
@login_required
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('admin_dashboard')  # Change to your department list view name
    else:
        form = DepartmentForm()
    return render(request, 'accounts/add_department.html', {'form': form})
@csrf_protect
@login_required
def get_account_types(request):
    profile_id = request.GET.get('profile_id')
    account_types = []
    if profile_id:
        profile = Profile.objects.get(pk=profile_id)
        account_types = list(profile.account_types.values_list('id', flat=True))
    return JsonResponse({'account_types': account_types})