from django.contrib.auth.models import User
from django.db import models

class Project(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    def __str__(self):
        return self.name

    def count_tasks_by_status(self):
        """
        Returns a dictionary with the count of tasks grouped by their status.
        """
        statuses = ['todo', 'in-progress', 'completed']
        counts = {status: self.tasks.filter(status=status).count() for status in statuses}
        return counts

