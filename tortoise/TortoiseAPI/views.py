from array import array
from binascii import rledecode_hqx
from datetime import date, datetime
import datetime
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pymysql import Date
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from TortoiseAPI.models import Plan,Promotions,CustomerGoals
from TortoiseAPI.serliazers import PlanSerializers,PromotionsSerializers,CustomerGoalsSerializers



@csrf_exempt
def planApi(request,id=0):
    status=1
    message=[]
    response_data=[]
    if request.method=='GET':
        today = datetime.datetime.now().date()
        plan = Plan.objects.all()
        for p in plan:
            try:          
                promotion=Promotions.objects.get(planID_id=getattr(p,'planID'))
                for promo in promotion:
                    if promotion.end_date:
                        end_date=datetime.date(promo.end_date)
                        start_date=datetime.date(promo.start_date)
                        if start_date <= today <= end_date:
                            plan_serializer = PlanSerializers(promo,many=True)
                            response_data.append({'plan':plan_serializer.data,'promotion_applied':1})
            except:
                response_data.append({'plan':json.dumps(p),'promotion_applied':0})  
        return JsonResponse(response_data,safe=False)
    if request.method=='POST':
        try:
            planName=request.POST['planName']
            amountOptions=request.POST['amountOptions']
            amountOptions=json.dumps(amountOptions)
            amountOptions=json.loads(amountOptions)
            amountOptions=eval(amountOptions)
            tenureOptions=request.POST['tenureOptions']
            tenureOptions=json.dumps(tenureOptions)
            tenureOptions=json.loads(tenureOptions)
            tenureOptions=eval(tenureOptions)
            benefitPercentage=int(request.POST['benefitPercentage'])
            benefitType=request.POST['benefitType']
            if not planName or planName=='':
                status=0
                message.append('Plan name cannot be empty')
            if not amountOptions or not isinstance(amountOptions,list):
                status=0
                message.append('Amount Options have to be an array')
            if amountOptions:
                for x in amountOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Amount Options has to contain Integers only and cannot be less than 0')
                        break
            if not tenureOptions or not isinstance(tenureOptions,list):
                status=0
                message.append('Tenure Options have to be an array')
            if tenureOptions:
                for x in tenureOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Tenure Options has to contain Integers only and cannot be less than 0')
                        break
            if not isinstance(benefitPercentage,int) or benefitPercentage <= 0:
                status=0
                message.append('Benefit Percentage has to be an integer value and cannot be less than 0')
            if not benefitType or benefitType=='':
                status=0
                message.append('Benefit Type cannot be empty')
        except Exception as e:
            return JsonResponse(e,safe=False)

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        plan=Plan()
        plan.planName=planName
        plan.amountOptions=amountOptions
        plan.tenureOptions=tenureOptions
        plan.benefitPercentage=benefitPercentage
        plan.benefitType=benefitType

        try:
            plan.save()
            return JsonResponse("Plan added successfully",safe=False) 
        except:
            return JsonResponse("Failed to Add",safe=False)
    if request.method=='PUT':
        try:
            planID=request.PUT['planID']
            planName=request.PUT['planName']
            amountOptions=request.PUT['amountOptions']
            amountOptions=json.dumps(amountOptions)
            amountOptions=json.loads(amountOptions)
            amountOptions=eval(amountOptions)
            tenureOptions=request.PUT['tenureOptions']
            tenureOptions=json.dumps(tenureOptions)
            tenureOptions=json.loads(tenureOptions)
            tenureOptions=eval(tenureOptions)
            benefitPercentage=int(request.PUT['benefitPercentage'])
            benefitType=request.PUT['benefitType']
            if not planID or isinstance(planID,int) or planID=='':
                status=0
                message.append('Plan ID has to be an integer value and cannot be empty')
            if planName and planName=='':
                status=0
                message.append('Plan name cannot be empty')
            if amountOptions and not isinstance(amountOptions,list):
                status=0
                message.append('Amount Options have to be an array')
            if amountOptions:
                for x in amountOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Amount Options has to contain Integers only and cannot be less than 0')
                        break
            if tenureOptions and not isinstance(tenureOptions,list):
                status=0
                message.append('Tenure Options have to be an array')
            if tenureOptions:
                for x in tenureOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Tenure Options has to contain Integers only and cannot be less than 0')
                        break
            if benefitPercentage and ( not isinstance(benefitPercentage,int) or benefitPercentage <= 0):
                status=0
                message.append('Benefit Percentage has to be an integer value and cannot be less than 0')
            if not benefitType or benefitType=='':
                status=0
                message.append('Benefit Type cannot be empty')
        except Exception as e:
            return JsonResponse(e,safe=False)

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        plan=Plan.objects.get(pk=planID)
        if planName:
            plan.planName=planName
        if amountOptions:
            plan.amountOptions=amountOptions
        if tenureOptions:
            plan.tenureOptions=tenureOptions
        if benefitPercentage:
            plan.benefitPercentage=benefitPercentage
        if benefitType:
            plan.benefitType=benefitType
        try:
            plan.save()
            return JsonResponse("Plan updated successfully",safe=False) 
        except:
            return JsonResponse("Failed to update plan",safe=False)
def promotionApi(request,planID=0):
    status=1
    message=[]
    response_data={}
    if request.method=='GET':
        promotion = Promotions.objects.all()
        promotion_serializer = PromotionsSerializers(promotion,many=True)
        return JsonResponse(promotion_serializer.data,safe=False)
    if request.method=='POST':
        planID=request.POST['planID']
        user_cap=request.POST['user_cap']
        promotion_start_date=request.POST['start_date']
        promotion_end_date=request.POST['end_date']
        if not planID or isinstance(planID,int) or planID<=0:
            status=0
            message.append('Plan ID has to be an integer value and cannot be empty')
        if not user_cap or isinstance(user_cap,int) or user_cap<=0:
            status=0
            message.append('User Capacity variable has to be an integer value and cannot be less than or equal to zero')
        if not promotion_start_date or promotion_start_date=='' or not isinstance(promotion_start_date,datetime.date):
            status=0
            message.append('Promotion start date cannot be empty and has to be of date format')
        if not promotion_end_date or promotion_end_date=='' or not isinstance(promotion_end_date,datetime.date):
            status=0
            message.append('Promotion end date cannot be empty and has to be of date format')
        
        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        promotion=Promotions.objects.get(planID_id=planID)
        for p in promotion:
            if promotion and promotion.end_date:
                end_date = datetime.date(promotion.end_date)
                if(end_date>=promotion_start_date):
                    status=0
                    message.append('A promotion already exists fir this plan ID, please delete this plan or change start date of Promotion')
                    break

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        new_promotion=Promotions()
        new_promotion.planID_id=planID
        new_promotion.user_cap=user_cap
        new_promotion.start_date=promotion_start_date
        new_promotion.end_date=promotion_end_date

        try:
            new_promotion.save()
            return JsonResponse("Promotion added successfully",safe=False) 
        except:
            return JsonResponse("Failed to add Promotion",safe=False)
        

