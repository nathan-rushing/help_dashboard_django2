from collections import defaultdict, Counter
import json
import math
import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Prefetch, F, Value, CharField
from django.db.models.functions import Coalesce

from .models import (
    Writers, Task, TaskWriter, MajorDocu, Version, Document
)
from .forms import (
    per_user_edit_Form, EditDocuForm, EditSectionForm, EditSubSectionForm,
    AddWriterForm, AssignTaskForm, AddSMEForm
)

@login_required
def home_test(request):
    # Annotate to handle nulls and sort accordingly
    writers = Writers.objects.annotate(
        sort_name=Coalesce('writer_name', Value('zzz'))  # 'zzz' ensures nulls go last
    ).order_by('sort_name')

    # task_writers = TaskWriter.objects.select_related('task', 'writer')
    task_writers = TaskWriter.objects.select_related('task', 'writer').order_by('-task__modified_at')


    writer_tasks_grouped = {}
    color_classes = [
        "color-blue", "color-green", "color-red", "color-purple",
        "color-cyan", "color-orange", "color-teal", "color-yellow"
    ]

    writer_color_classes = {}
    for i, writer in enumerate(writers):
        writer_color_classes[writer.pk] = color_classes[i % len(color_classes)]

        grouped_by_doc = defaultdict(list)
        for tw in task_writers:
            if tw.writer_id == writer.pk:
                grouped_by_doc[tw.task.document].append(tw)
        writer_tasks_grouped[writer.pk] = dict(grouped_by_doc)

    version = Version.objects.first()

    ctx = {
        'writers': writers,
        'writer_tasks_grouped': writer_tasks_grouped,
        'writer_color_classes': writer_color_classes,
        'version': version,
        'can_edit': request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff),
    }
    return render(request, 'online_help/home_test.html', ctx)

@login_required
def tasks_by_color(request, writer_pk, color):
    writer = get_object_or_404(Writers, pk=writer_pk)
    tasks = TaskWriter.objects.filter(
        writer=writer,
        task__color=color
    ).select_related('task').order_by('task__document', '-task__modified_at')

    return render(request, 'online_help/tasks_by_color.html', {
        'writer': writer,
        'color': color,
        'tasks': tasks,
    })

@login_required
def per_user_test(request, writer_pk):
    writer = get_object_or_404(Writers, pk=writer_pk)
    tasks = TaskWriter.objects.filter(writer=writer).select_related('task').order_by('task__document', '-task__modified_at')

    grouped_tasks = defaultdict(list)
    color_counts = Counter()

    for tw in tasks:
        grouped_tasks[tw.task.document].append(tw)
        color_counts[tw.task.color] += 1

    total_tasks = sum(color_counts.values())
    # document_task_counts = {doc: len(tws) for doc, tws in grouped_tasks.items()}
    document_task_counts = {str(doc): len(tws) for doc, tws in grouped_tasks.items()}

    return render(request, 'online_help/per_user_test.html', {
        'writer': writer,
        'grouped_tasks': dict(grouped_tasks),
        'color_counts': dict(color_counts),
        'total_tasks': total_tasks,
        'document_task_counts_json': json.dumps(document_task_counts),
    })

@login_required
def per_user_edit_test(request, writer_pk, task_pk):
    writer = get_object_or_404(Writers, pk=writer_pk)
    task = get_object_or_404(Task, pk=task_pk)

    if request.method == 'POST':
        form = per_user_edit_Form(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('online_help:per_user_test', writer_pk=writer.pk)
            # return redirect('online_help:per_user_edit_test', writer_pk=writer.pk, task_pk=task.pk)
    else:
        form = per_user_edit_Form(instance=task)

    return render(request, 'online_help/per_user_edit_test.html', {
        'form': form,
        'writer': writer,
        'task': task
    })

@login_required
def per_subsection_test(request, writer_pk, task_pk):
    # Get the writer
    writer = get_object_or_404(Writers, pk=writer_pk)

    # Get the task
    task = get_object_or_404(Task, pk=task_pk)

    # Render the template
    return render(request, 'online_help/per_subsection_test.html', {
        'writer': writer,
        'task': task
    })

@login_required
def per_subsection_edit_test(request, writer_pk, task_pk):
    writer = get_object_or_404(Writers, pk=writer_pk)
    task = get_object_or_404(Task, pk=task_pk)

    if request.method == 'POST':
        form = per_user_edit_Form(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('online_help:per_subsection_test', writer_pk=writer.pk, task_pk=task.pk)
    else:
        form = per_user_edit_Form(instance=task)

    return render(request, 'online_help/per_subsection_edit_test.html', {
        'form': form,
        'writer': writer,
        'task': task
    })


@require_POST
@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def update_version(request):
    new_version = request.POST.get('version')
    if new_version:
        version_obj, _ = Version.objects.get_or_create(id=1)
        version_obj.number = new_version
        version_obj.save()
        return JsonResponse({'status': 'success', 'version': new_version})
    return JsonResponse({'status': 'error', 'message': 'No version provided'}, status=400)

@require_POST
@login_required
def verify_password(request):
    password = request.POST.get('password')
    user = authenticate(username=request.user.username, password=password)
    if user:
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid password'}, status=403)

@login_required
def tasks_test(request):
    # tasks = Task.objects.all().order_by('document')
    tasks = Task.objects.all()
    # tasks = Task.objects.all().order_by('-modified_at')
    # task_writers = TaskWriter.objects.select_related('task', 'writer')
    task_writers = TaskWriter.objects.select_related('task', 'writer').order_by('-task__modified_at')

    # Group writers by task
    writers_by_task_id = defaultdict(list)
    for tw in task_writers:
        writers_by_task_id[tw.task_id].append(tw)

    # Group tasks by document
    grouped_by_document = defaultdict(list)
    for task in tasks:
        grouped_by_document[task.document].extend(writers_by_task_id.get(task.id, []))

    ctx = {
        'grouped_documents': dict(grouped_by_document),
    }
    return render(request, 'online_help/tasks_test.html', ctx)

@login_required
def per_documentation_test(request, document_pk):
    # Get one task to extract the document name
    reference_task = get_object_or_404(Task, pk=document_pk)
    document_name = reference_task.document

    # Get all tasks with the same document name
    tasks = Task.objects.filter(document=document_name)

    # Get one task per unique section
    seen_sections = set()
    unique_section_tasks = []
    for task in tasks:
        if task.section not in seen_sections:
            seen_sections.add(task.section)
            unique_section_tasks.append(task)

    return render(request, 'online_help/per_documentation_test.html', {
        'document_name': document_name,
        'document_pk': document_pk,
        'sections': unique_section_tasks,  # list of Task objects
    })

@login_required
def per_documentation_test2(request, document_pk):
    task = get_object_or_404(Task, pk=document_pk)
    tasks = Task.objects.filter(document=task.document)

    # Get one task per unique section
    seen_sections = set()
    unique_section_tasks = []
    for t in tasks:
        if t.section not in seen_sections:
            seen_sections.add(t.section)
            unique_section_tasks.append(t)

    ctx = {
        'document_name': task.document,
        'sections': unique_section_tasks,  # Now these are Task objects
        'document_pk': document_pk,
    }
    return render(request, 'online_help/per_documentation_test.html', context=ctx)




@login_required
def per_section_test(request, document_pk, section_pk):
    reference_task = get_object_or_404(Task, pk=section_pk)
    document_name = reference_task.document
    section_name = reference_task.section

    # Fetch all tasks for the same document and section
    tasks = Task.objects.filter(document=document_name, section=section_name).prefetch_related(
        Prefetch('taskwriter_set', queryset=TaskWriter.objects.select_related('writer'))
    )

    # Group tasks by sub_section to avoid duplication
    grouped_tasks = defaultdict(lambda: {
        'writers': [],
        'comments': '',
        'color': '',
        'completion': '',
        'id': None,
    })

    for task in tasks:
        key = task.sub_section
        grouped_tasks[key]['id'] = task.id
        grouped_tasks[key]['comments'] = task.comments
        grouped_tasks[key]['color'] = task.color
        grouped_tasks[key]['completion'] = task.completion
        grouped_tasks[key]['writers'].extend([tw.writer.writer_name for tw in task.taskwriter_set.all()])

    # Remove duplicate writer names
    for task in grouped_tasks.values():
        task['writers'] = list(set(task['writers']))

    return render(request, 'online_help/per_section_test.html', {
        'document_name': document_name,
        'section_name': section_name,
        'tasks': grouped_tasks.items(),  # key-value pairs: sub_section -> task data
        'document_pk': document_pk,
        'section_pk': section_pk,
    })


@login_required
def per_section_test2(request, document_pk, section_pk):
    reference_task = get_object_or_404(Task, pk=section_pk)
    document_name = reference_task.document
    section_name = reference_task.section

    # Fetch all tasks for the same document and section
    tasks = Task.objects.filter(document=document_name, section=section_name).prefetch_related(
        Prefetch('taskwriter_set', queryset=TaskWriter.objects.select_related('writer'))
    )

    # Group tasks by sub_section to avoid duplication
    grouped_tasks = defaultdict(lambda: {
        'writers': [],
        'comments': '',
        'color': '',
        'completion': '',
        'id': None,
    })

    for task in tasks:
        key = task.sub_section
        grouped_tasks[key]['id'] = task.id
        grouped_tasks[key]['comments'] = task.comments
        grouped_tasks[key]['color'] = task.color
        grouped_tasks[key]['completion'] = task.completion
        grouped_tasks[key]['writers'].extend([tw.writer.writer_name for tw in task.taskwriter_set.all()])

    # Remove duplicate writer names
    for task in grouped_tasks.values():
        task['writers'] = list(set(task['writers']))

    return render(request, 'online_help/per_section_test.html', {
        'document_name': document_name,
        'section_name': section_name,
        'tasks': grouped_tasks.items(),  # key-value pairs: sub_section -> task data
        'document_pk': 1,
        'section_pk': section_pk,
    })



@login_required
def per_subsection_task_test(request, document_pk, section_pk, subsection_pk):
    reference_task = get_object_or_404(Task, pk=subsection_pk)

    # Normalize SME value
    if reference_task.SME is None or (isinstance(reference_task.SME, float) and math.isnan(reference_task.SME)):
        reference_task.SME = 'nan'
        reference_task.save()

    document_name = reference_task.document
    section_name = reference_task.section
    sub_section_name = reference_task.sub_section
    sme_name = reference_task.SME

    # Get all writers for tasks with the same document, section, and sub_section
    task_writers = TaskWriter.objects.select_related('writer', 'task').filter(
        task__document=document_name,
        task__section=section_name,
        task__sub_section=sub_section_name,
    )

    form = AddWriterForm()
    sme_form = AddSMEForm()

    if request.method == 'POST':
        if 'edit_sme_form' in request.POST:
            sme_form = AddSMEForm(request.POST)
            if sme_form.is_valid():
                reference_task.SME = sme_form.cleaned_data['sme']
                reference_task.save()
                messages.success(request, f"SME updated to '{reference_task.SME}'.")
                return redirect(request.path_info)
        else:
            form = AddWriterForm(request.POST)
            if form.is_valid():
                writer = form.cleaned_data['writer']
                TaskWriter.objects.get_or_create(task=reference_task, writer=writer)
                messages.success(request, f"Writer '{writer.writer_name}' added successfully.")
                return redirect(request.path_info)

    # Handle writer removal from all matching tasks
    writer_to_remove = request.GET.get('remove_writer')
    if writer_to_remove:
        try:
            writer = Writers.objects.get(writer_name=writer_to_remove)
            TaskWriter.objects.filter(
                task__document=document_name,
                task__section=section_name,
                task__sub_section=sub_section_name,
                writer=writer
            ).delete()
            messages.success(request, f"Writer '{writer_to_remove}' removed successfully.")
            return redirect(request.path_info)
        except Writers.DoesNotExist:
            messages.error(request, f"Writer '{writer_to_remove}' not found.")

    return render(request, 'online_help/per_subsection_task_test.html', {
        'document_name': document_name,
        'section_name': section_name,
        'sub_section_name': sub_section_name,
        'task_writers': task_writers,
        'form': form,
        'sme_form': sme_form,
        'sme': reference_task.SME,
        'document_pk': document_pk,
        'section_pk': section_pk,
    })

@login_required
def per_subsection_task_test2(request, subsection_pk):
    reference_task = get_object_or_404(Task, pk=subsection_pk)

    # Normalize SME value
    if reference_task.SME is None or (isinstance(reference_task.SME, float) and math.isnan(reference_task.SME)):
        reference_task.SME = 'nan'
        reference_task.save()
    
    document_name = reference_task.document
    section_name = reference_task.section
    sub_section_name = reference_task.sub_section
    sme_name = reference_task.SME

    # Get all writers for tasks with the same document, section, and sub_section
    task_writers = TaskWriter.objects.select_related('writer', 'task').filter(
        task__document=document_name,
        task__section=section_name,
        task__sub_section=sub_section_name
    )

    form = AddWriterForm()
    sme_form = AddSMEForm()

    # Handle form submission
    if request.method == 'POST':
        if 'edit_sme_form' in request.POST:
            sme_form = AddSMEForm(request.POST)
            if sme_form.is_valid():
                reference_task.SME = sme_form.cleaned_data['sme']
                reference_task.save()
                messages.success(request, f"SME updated to '{reference_task.SME}'.")
                return redirect(request.path_info)

        else:
            form = AddWriterForm(request.POST)
            if form.is_valid():
                writer = form.cleaned_data['writer']
                TaskWriter.objects.get_or_create(task=reference_task, writer=writer)
                messages.success(request, f"Writer '{writer.writer_name}' added successfully.")
                return redirect(request.path_info)

    # Handle removal via GET parameter (?remove_writer=Name)
    writer_to_remove = request.GET.get('remove_writer')
    if writer_to_remove:
        try:
            writer = Writers.objects.get(writer_name=writer_to_remove)
            TaskWriter.objects.filter(
                task__document=document_name,
                task__section=section_name,
                task__sub_section=sub_section_name,
                writer=writer
            ).delete()
            messages.success(request, f"Writer '{writer_to_remove}' removed successfully.")
            return redirect(request.path_info)
        except Writers.DoesNotExist:
            messages.error(request, f"Writer '{writer_to_remove}' not found.")

    return render(request, 'online_help/per_subsection_task_test.html', {
        'document_name': document_name,
        'section_name': section_name,
        'sub_section_name': sub_section_name,
        'task_writers': task_writers,
        'form': form,
        'sme_form': sme_form,
        'sme': reference_task.SME,
        # 'document_pk': document_pk,
        # 'section_pk': section_pk,
    })

# @login_required
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or 'online_help:home_test'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    next_url = request.GET.get('next', '')
    return render(request, 'online_help/login.html', {'next': next_url})

@login_required
def logout_view(request):
    logout(request)
    return redirect('online_help:login')

@login_required
def tasks_edit_test(request):
    all_tasks = Task.objects.all().order_by('document')
    
    # Use a set to track unique document names
    seen_documents = set()
    unique_tasks = []

    for task in all_tasks:
        if task.document not in seen_documents:
            unique_tasks.append(task)
            seen_documents.add(task.document)


    ctx = {
        'tasks': unique_tasks,
        'first_task_id': unique_tasks[0].id if unique_tasks else None
    }

    return render(request, 'online_help/tasks_edit_test.html', context=ctx)


@login_required
def export_taskwriters_excel(request):
    # Fetch data
    queryset = TaskWriter.objects.select_related('task', 'writer').values(
        'writer__writer_name',
        'task__document',
        'task__section',
        'task__sub_section',
        'task__completion',
        'task__color',
        'task__SME',
        'task__comments',)

    # Convert to DataFrame
    df = pd.DataFrame(list(queryset))
    df.rename(columns={
        'writer__writer_name': 'Writer',
        'task__document': 'Document',
        'task__section': 'Section',
        'task__sub_section': 'Subsection',
        'task__completion': 'Completion',
        'task__color': 'Color',
    }, inplace=True)

    # Create Excel file in memory
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=taskwriters_export.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Task Writers')

    return response


@login_required
def documentation_edit_test(request):
    all_tasks = Task.objects.all().order_by('document')

    seen_documents = set()
    unique_tasks = []

    for task in all_tasks:
        if task.document not in seen_documents:
            unique_tasks.append(task)
            seen_documents.add(task.document)

    if request.method == 'POST':
        form = EditDocuForm(request.POST)
        if form.is_valid():
            document_name = form.cleaned_data['document']

            # Get or create the Document instance
            document, _ = Document.objects.get_or_create(title=document_name)

            # Now create the Task with the Document instance
            new_task = Task.objects.create(
                document=document,
                section='nan',
                sub_section='nan',
                comments='',
                SME='nan',
                color='',
                completion='0%'
            )

            default_writer = Writers.objects.filter(writer_name='nan').first()
            if default_writer:
                TaskWriter.objects.create(task=new_task, writer=default_writer)

            return redirect('online_help:documentation_edit_test')

    else:
        form = EditDocuForm()

    return render(request, 'online_help/documentation_edit_test.html', {
        'tasks': unique_tasks,
        'form': form,
        'first_task_id': unique_tasks[0].id if unique_tasks else None,
    })


@login_required
def section_edit_test(request, document_pk):
    # Get one task to extract the document name
    reference_task = get_object_or_404(Task, pk=document_pk)
    document_name = reference_task.document

    # Get all tasks with the same document name
    tasks = Task.objects.filter(document=document_name)

    # Get one task per unique section
    seen_sections = set()
    unique_section_tasks = []
    for task in tasks:
        if task.section not in seen_sections:
            seen_sections.add(task.section)
            unique_section_tasks.append(task)

    if request.method == 'POST':
        form = EditSectionForm(request.POST)
        if form.is_valid():
            section = form.cleaned_data['section']
            # subsection = form.cleaned_data['subsection']
            subsection = 'nan'  # Default value for subsection
            # writer = form.cleaned_data['writer']
            # color = form.cleaned_data['color']

            # Create a new Task entry
            Task.objects.create(
                document=document_name,
                section=section,
                sub_section=subsection,
                # writer=writer,
                # color=color
            )

            return redirect('online_help:section_edit_test', document_pk=document_pk)
    else:
        form = EditSectionForm()

    # Always return a response
    return render(request, 'online_help/section_edit_test.html', {
        'form': form,
        'document_name': document_name,
        'document_pk': document_pk,
        'sections': unique_section_tasks,
    })

@require_POST
def delete_section(request, document_pk, section_name):
    # Delete all tasks with the same document and section
    Task.objects.filter(document__pk=document_pk, section=section_name).delete()
    # Task.objects.filter(document=document_pk, section=section_name).delete()

    return redirect('online_help:section_edit_test', document_pk=document_pk)

@login_required
def per_section_edit_test(request, section_pk):
    section_task = get_object_or_404(Task, pk=section_pk)
    section_name = section_task.section
    document_name = section_task.document

    subsections = Task.objects.filter(section=section_name)

    if request.method == 'POST':
        form = EditSubSectionForm(request.POST)
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.section = section_name
            new_sub.sub_section = form.cleaned_data['sub_section']
            new_sub.document = document_name
            new_sub.SME = 'nan'
            new_sub.color = form.cleaned_data['color']
            # new_sub.color = section_task.color
            new_sub.comments = 'nan'
            new_sub.completion = '0%'
            new_sub.save()

            # ✅ Create TaskWriter entry using selected writer
            selected_writer = form.cleaned_data['writer']
            TaskWriter.objects.create(task=new_sub, writer=selected_writer)

            return redirect('online_help:per_section_edit_test', section_pk=section_pk)
    else:
        form = EditSubSectionForm()

    return render(request, 'online_help/per_section_edit_test.html', {
        'section_name': section_name,
        'subsections': subsections,
        'form': form,
        'section_pk': section_pk,
        'document_pk': section_task.pk,  # Use section_task.pk as document_pk

    })

def delete_subsection(request, section_pk, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    task.delete()
    return redirect('online_help:per_section_edit_test', section_pk=section_pk)

def delete_document(request, document_pk):
    task = get_object_or_404(Task, pk=document_pk)
    Task.objects.filter(document=task.document).delete()
    return redirect('online_help:documentation_edit_test')


@login_required
def assign_task_test(request):
    if request.method == 'POST':
        form = AssignTaskForm(request.POST)
        print('we are before form.is_valid()')

        if form.is_valid():
            document = form.cleaned_data['document']
            section = form.cleaned_data['section']
            sub_section = form.cleaned_data['sub_section']
            writer = form.cleaned_data['writer']

            print("Form submitted with:", document, section, sub_section, writer)

            # Try to find the first matching task
            task = Task.objects.filter(
                document=document,
                section=section,
                sub_section=sub_section
            ).first()

            if not task:
                print("No matching task found.")
                form.add_error(None, "Task not found for the selected document, section, and subsection.")
            else:
                obj, created = TaskWriter.objects.get_or_create(task=task, writer=writer)
                print("TaskWriter created:", created)
                return redirect('online_help:tasks_test')  # Redirect to task list after successful assignment

        else:
            print("Form is invalid:", form.errors)

    else:
        form = AssignTaskForm()

    return render(request, 'online_help/assign_task_test.html', {'form': form})


def load_sections(request):
    document = request.GET.get('document')
    sections = Task.objects.filter(document=document).values_list('section', flat=True).distinct()
    return JsonResponse(list(sections), safe=False)

def load_subsections(request):
    section = request.GET.get('section')
    subsections = Task.objects.filter(section=section).values_list('sub_section', flat=True).distinct()
    return JsonResponse(list(subsections), safe=False)



from .models import Task, Document
from django.db.models import F

@login_required
def view_all(request):
    document_id = request.GET.get('document')
    color = request.GET.get('color')

    tasks = Task.objects.select_related('document')

    if document_id:
        tasks = tasks.filter(document_id=document_id)
    if color:
        tasks = tasks.filter(color=color)

    documents = Document.objects.all()
    colors = Task.objects.values_list('color', flat=True).distinct()

    return render(request, 'online_help/view_all.html', {
        'tasks': tasks,
        'documents': documents,
        'colors': colors,
    })
