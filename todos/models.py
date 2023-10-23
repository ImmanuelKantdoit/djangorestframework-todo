from helpers.models import TrackingModel
from django.db import models
from authentication.models import User

class Todo(TrackingModel):
    title = models.CharField(max_length=255)
    desc = models.TextField()
    is_complete = models.BooleanField(default=False)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['title']  # Define the 'ordering' attribute as a list with one field, 'title'

    def __str__(self):
        return self.title
