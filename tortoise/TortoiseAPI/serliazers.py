from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from TortoiseAPI.models import Plan,Promotions,CustomerGoals

class PlanSerializers(serializers.ModelSerializer):
    class Meta:
        model=Plan
        fields=('planID','planName','amountOptions','tenureOptions','benefitPercentage','benefitType','created_at','updated_at')

class PromotionsSerializers(serializers.ModelSerializer):
    class Meta:
        model=Promotions
        fields=('promotionID','user_cap','start_date','end_date','created_at','updated_at','planID_id')

class CustomerGoalsSerializers(serializers.ModelSerializer):
    class Meta:
        model=CustomerGoals
        fields=('ID','userID','selectedAmount','selectedTenure','depositedAmount','benefitPercentage','created_at','updated_at','planID_id')