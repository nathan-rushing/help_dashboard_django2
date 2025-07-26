# Create your models here.
from django.db import models
class Writers(models.Model):
    writer_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.writer_name }"
        # return f"{self.writer_name } - {self.id}"

from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='tasks')
    section = models.CharField(max_length=255)
    sub_section = models.CharField(max_length=255)
    comments = models.TextField()
    SME = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=50)
    completion = models.CharField(max_length=100, default='0%')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.id} - {self.document.title}: {self.section} - {self.sub_section}"

class TaskWriter(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    writer = models.ForeignKey(Writers, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('task', 'writer')

    def __str__(self):
        return f"{self.writer.writer_name} ({self.writer.id}) assigned for {self.task.document}. ID: {self.task.id}"

class MajorDocu(models.Model):
    projects = models.CharField(max_length=255)
    SME = models.CharField(max_length=255)
    support = models.ForeignKey(Writers, on_delete=models.CASCADE, related_name='supported_docs')
    writer = models.ForeignKey(Writers, on_delete=models.CASCADE, related_name='written_docs')

    def __str__(self):
        return f"MajorDocu {self.id} - {self.projects}"

class Version(models.Model):
    number = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number


# input this when prompted in makemigrations: 
# choose option 1
# timezone.now
