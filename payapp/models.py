from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Money(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    money = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)  # Changed to DecimalField
    currency = models.CharField(max_length=10, default='GBP')  # Default currency set to GBP

    def __str__(self):
        return str(self.money) + ' ' + self.currency

class MoneyTransfer(models.Model):
    enter_your_username = models.CharField(max_length=50)
    enter_destination_username = models.CharField(max_length=50)
    enter_amount_to_transfer = models.IntegerField()

    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username}\n'
        details += f'Destination username     : {self.enter_destination_username}\n'
        details += f'Amount To Transfer         : {self.enter_amount_to_transfer}\n'
        return details



class TransactionHistory(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    sender_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    receiver_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sender_currency = models.CharField(max_length=10, default='GBP')
    receiver_currency = models.CharField(max_length=10, default='GBP')
    timestamp = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

class MoneyRequest(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    ]
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)

    sender_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    receiver_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sender_currency = models.CharField(max_length=10, default='GBP')
    receiver_currency = models.CharField(max_length=10, default='GBP')

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    timestamp = models.DateTimeField(auto_now_add=True)