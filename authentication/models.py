from django.db import models


class SignUpApprovalQueue(models.Model):
    requested_date = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

