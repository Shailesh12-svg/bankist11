from django.db import models

class Account(models.Model):
    owner = models.CharField(max_length=100)
    pin = models.CharField(max_length=4)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    movements = models.JSONField(default=list)

    def __str__(self):
        return self.owner

    