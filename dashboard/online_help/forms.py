from django import forms
from .models import Task, Writers, TaskWriter, Document

from django import forms
from .models import Writers, Task

COLOR_CHOICES = [
    ('green', 'green'),
    ('yellow', 'yellow'),
    ('grey', 'grey'),
    ('white', 'white'),
]

class per_user_edit_Form(forms.ModelForm):
    color = forms.ChoiceField(choices=COLOR_CHOICES, label='Color')
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 100}),
        label='Comments'
    )
    completion = forms.CharField(
        required=True,
        max_length=100,
        label='Completion',
        widget=forms.TextInput()
    )

    class Meta:
        model = Task
        fields = ['color', 'comments', 'completion']


# from django import forms
# from .models import Documentation

# class EditDocuForm(forms.ModelForm):
#     class Meta:
#         # model = Documentation
#         fields = ['documentation', 'section', 'subsection', 'writer', 'color']
#         widgets = {
#             'documentation': forms.TextInput(attrs={'placeholder': 'Documentation'}),
#             'section': forms.TextInput(attrs={'placeholder': 'Section'}),
#             'subsection': forms.TextInput(attrs={'placeholder': 'Subsection'}),
#             'writer': forms.TextInput(attrs={'placeholder': 'Writer'}),
#             'color': forms.TextInput(attrs={'placeholder': 'Color'}),
#         }


class EditDocuForm(forms.Form):
    document = forms.CharField(label='Document Name', required=False, max_length=255)
    # section = forms.CharField(required=False, max_length=255)
    # subsection = forms.CharField(required=False, max_length=255)
    # writer = forms.CharField(required=False, max_length=255)
    # color = forms.CharField(required=False, max_length=50)

# class EditSectionForm(forms.Form):
    # section = forms.CharField(required=False, max_length=255)
    # subsection = forms.CharField(required=False, max_length=255)
    # writer = forms.CharField(required=False, max_length=255)
    # color = forms.CharField(required=False, max_length=50)

class EditSectionForm(forms.ModelForm):
    # writer = forms.ModelChoiceField(queryset=Writers.objects.all(), required=True)

    class Meta:
        model = Task
        # fields = ['section', 'writer']
        fields = ['section']


from django import forms
from .models import Task, Writers

class EditSubSectionForm(forms.ModelForm):
    writer = forms.ModelChoiceField(queryset=Writers.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ['sub_section', 'color']  # Use actual model field names
        labels = {
            'sub_section': 'Subsection',
            'color': 'Color',
        }
        widgets = {
            'sub_section': forms.TextInput(attrs={'placeholder': 'Enter subsection name'}),
            'color': forms.Select(choices=COLOR_CHOICES, attrs={'placeholder': 'Enter color'}),
        }

class AddWriterForm(forms.Form):
    writer = forms.ModelChoiceField(
        queryset=Writers.objects.all(),
        required=True,
        label='Select Writer',
        empty_label="Choose a writer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AssignTaskForm(forms.Form):
    document = forms.ChoiceField(
        label="Document",
        required=True,
        widget=forms.Select(attrs={'id': 'id_document', 'class': 'form-control'})
    )
    section = forms.ChoiceField(
        label="Section",
        required=True,
        widget=forms.Select(attrs={'id': 'id_section', 'class': 'form-control'})
    )
    sub_section = forms.ChoiceField(
        label="Subsection",
        required=True,
        widget=forms.Select(attrs={'id': 'id_sub_section', 'class': 'form-control'})
    )
    writer = forms.ModelChoiceField(
        queryset=Writers.objects.all(),
        label="Writer",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # sme = forms.CharField(
    #     label="SME (optional)",
    #     required=False,
    #     widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SME name (optional)'})
    # )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # documents = Task.objects.values_list('document', flat=True).distinct()
        # self.fields['document'].choices = [('', 'Select document')] + [(doc, doc) for doc in documents]

        documents = Document.objects.filter(id__in=Task.objects.values_list('document', flat=True).distinct())
        self.fields['document'].choices = [('', 'Select document')] + [(doc.id, doc.title) for doc in documents]

        self.fields['section'].choices = [('', 'Select section')]
        self.fields['sub_section'].choices = [('', 'Select subsection')]

        if 'document' in self.data:
            document = self.data.get('document')
            sections = Task.objects.filter(document=document).values_list('section', flat=True).distinct()
            self.fields['section'].choices += [(s, s) for s in sections]

        if 'section' in self.data:
            section = self.data.get('section')
            subsections = Task.objects.filter(section=section).values_list('sub_section', flat=True).distinct()
            self.fields['sub_section'].choices += [(s, s) for s in subsections]

class AddSMEForm(forms.Form):
    sme = forms.CharField(label="Enter SME Name", max_length=255)
