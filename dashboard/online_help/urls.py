from django.urls import path
from . import views

app_name = 'online_help'
urlpatterns = [  
    # Home and user-related paths
    path('', views.home_test, name='home_test'),
    path('home_test/', views.home_test, name='home_test'),
    path('home_test/per_user_test/<int:writer_pk>/', views.per_user_test, name='per_user_test'),
    path('home_test/per_user_test/<int:writer_pk>/color/<str:color>/', views.tasks_by_color, name='tasks_by_color'),
    path('home_test/per_user_test/<int:writer_pk>/per_subsection_test/<int:task_pk>/', views.per_subsection_test, name='per_subsection_test'),
    path('home_test/per_user_test/<int:writer_pk>/per_subsection_test/<int:task_pk>/per_user_edit_test/', views.per_subsection_edit_test, name='per_subsection_edit_test'),
    path('home_test/per_user_test/<int:writer_pk>/per_user_edit_test/<int:task_pk>/', views.per_user_edit_test, name='per_user_edit_test'),

    # Tasks main and assignment
    path('tasks_test/', views.tasks_test, name='tasks_test'),
    path('tasks_test/assign_tasks_test/', views.assign_task_test, name='assign_task_test'),

    # Documentation-related paths
    path('tasks_test/per_documentation_test/<int:document_pk>/', views.per_documentation_test, name='per_documentation_test'),
    path('tasks_test/per_documentation_test/<int:document_pk>/documentation_edit_test/', views.documentation_edit_test, name='documentation_edit_test'),
    path('tasks_test/per_documentation_test/<int:document_pk>/per_section_test/<int:section_pk>/', views.per_section_test, name='per_section_test'),
    path('tasks_test/per_documentation_test/<int:document_pk>/per_section_test/<int:section_pk>/per_subsection_task_test/<int:subsection_pk>/', views.per_subsection_task_test, name='per_subsection_task_test'),
    path('tasks_test/per_documentation_test/<int:document_pk>/section_edit_test', views.section_edit_test, name='section_edit_test'),
    path('tasks_test/per_documentation_test/<int:document_pk>/section_edit_test/delete/<str:section_name>/', views.delete_section, name='delete_section'),

    # Section-related paths
    path('tasks_test/per_section_test/<int:section_pk>/', views.per_section_test2, name='per_section_test2'),
    path('tasks_test/per_section_test/<int:section_pk>/per_section_edit_test', views.per_section_edit_test, name='per_section_edit_test'),
    path('tasks_test/per_section_test/<int:section_pk>/per_section_edit_test/delete/<int:task_pk>/', views.delete_subsection, name='delete_subsection'),

    # Subsection-related paths
    path('tasks_test/per_subsection_task_test/<int:subsection_pk>/', views.per_subsection_task_test2, name='per_subsection_task_test2'),

    # Tasks edit and documentation edit
    path('tasks_test/tasks_edit_test/', views.tasks_edit_test, name='tasks_edit_test'),
    path('tasks_test/tasks_edit_test/documentation_edit_test/', views.documentation_edit_test, name='documentation_edit_test'),
    path('tasks_test/tasks_edit_test/per_documentation_test/<int:document_pk>/', views.per_documentation_test2, name='per_documentation_test2'),

    # Document deletion
    path('tasks_test/documentation_edit_test/<int:document_pk>/delete/', views.delete_document, name='delete_document'),

    # Utility and authentication
    path('update-version/', views.update_version, name='update_version'),
    path('verify-password/', views.verify_password, name='verify_password'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # AJAX endpoints
    path('ajax/load-sections/', views.load_sections, name='ajax_load_sections'),
    path('ajax/load-subsections/', views.load_subsections, name='ajax_load_subsections'),

    path('export-taskwriters/', views.export_taskwriters_excel, name='export_taskwriters_excel'),

    path('view_all/', views.view_all, name='view_all'),

    # rename the item in document, section, and subsection
    path('documents/<int:document_pk>/rename/', views.rename_document, name='rename_document'),
    path('sections/<int:task_pk>/rename/', views.rename_section, name='rename_section'),
    path('subsections/<int:task_pk>/rename/', views.rename_subsection, name='rename_subsection'),

]
