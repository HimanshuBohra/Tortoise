from pyexpat import model
from django.db import models

# Create your models here.

class Plan(models.Model):

    class benefitType(models.TextChoices):
        CASHBACK = 'Cashback'
        EXTRAVOUCHER = 'ExtraVoucher'
        DISCOUNT = 'Discount' 
    


    planID = models.AutoField(primary_key=True,auto_created = True)
    planName = models.CharField(max_length=100)
    amountOptions = models.CharField(max_length=200)
    tenureOptions = models.CharField(max_length=200)
    benefitPercentage = models.IntegerField(max_length=5)
    benefitType = models.CharField(
        max_length=50,
        choices=benefitType.choices,
        default=benefitType.CASHBACK
    )
    status = models.SmallIntegerField(max_length=3,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Promotions(models.Model):
    promotionID = models.AutoField(primary_key=True,auto_created = True)
    planID = models.ForeignKey(Plan,on_delete=models.CASCADE)
    user_cap = models.IntegerField(max_length=5)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.SmallIntegerField(max_length=3,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerGoals(models.Model):
    ID = models.AutoField(primary_key=True,auto_created = True)
    planID = models.ForeignKey(Plan,on_delete=models.CASCADE)
    promotionID = models.ForeignKey(Promotions, on_delete=models.CASCADE)
    userID = models.IntegerField(max_length=10)
    selectedAmount = models.IntegerField(max_length=10)
    selectedTenure = models.IntegerField(max_length=10)
    depositedAmount = models.IntegerField(max_length=10)
    benefitPercentage = models.IntegerField(max_length=5)
    status = models.SmallIntegerField(max_length=3,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

