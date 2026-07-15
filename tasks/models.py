from django.db import models

from common.models import BaseModel
from account.models import User
from crm.models import Contact, Deal



class Task(BaseModel):
    description = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.description



class Activity(BaseModel):
    TYPE_CHOICES = [
        ('call', "Qo'ng'iroq"),
        ('meeting', 'Uchrashuv'),
        ('email', 'Email'),
        ('note', 'Izoh'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    note = models.TextField()

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.contact}"