from array import array
from binascii import rledecode_hqx
from datetime import date, datetime
import datetime
import json
import re
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pymysql import Date
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from TortoiseAPI.models import Plan,Promotions,CustomerGoals
from TortoiseAPI.serliazers import PlanSerializers,PromotionsSerializers,CustomerGoalsSerializers
from django.db.models import Q



@csrf_exempt
def planApi(request):
    status=1
    message=[]
    response_data={}
    if request.method=='GET':
        today = datetime.datetime.now().date()
        plan = Plan.objects.raw("select planID,planName,amountOptions,tenureOptions,benefitPercentage,benefitType,promotions.promotionID,promotions.count,promotions.user_cap , '' as promotion_status from tortoiseapi_plan left join (select tortoiseapi_promotions.promotionID ,tortoiseapi_promotions.planID_id,tortoiseapi_promotions.user_cap, count(tortoiseapi_customergoals.promotionID_id) as count from tortoiseapi_promotions left join tortoiseapi_customergoals on tortoiseapi_promotions.promotionID = tortoiseapi_customergoals.promotionID_id where start_date<=DATE(now()) and end_date>=DATE(now()) and tortoiseapi_promotions.status = 1 and tortoiseapi_customergoals.status=1 group by tortoiseapi_customergoals.promotionID_id) as promotions on promotions.planID_id = tortoiseapi_plan.planID where tortoiseapi_plan.status=1")
        for p in plan:
            if p.promotionID and p.count < p.user_cap:
                p.promotion_status=1
            else:
                p.promotion_status=0
                p.promotionID=''
            
        plan_serializedData = [ {'planID': p.planID,'planName': p.planName,'amountOptions':p.amountOptions,'tenureOptions':p.tenureOptions,'benefitPercentage':p.benefitPercentage,'benefitType':p.benefitType,'promotion_applied':p.promotion_status,'promotionID':p.promotionID} for p in plan]
        count=len(plan_serializedData)
        return JsonResponse({'status':1,'count':count,'data':plan_serializedData},safe=False)
    if request.method=='POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            planName=data['planName']
            amountOptions=data['amountOptions']
            tenureOptions=data['tenureOptions']
            benefitPercentage=data['benefitPercentage']
            benefitType=data['benefitType']
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
                duplicate_flag = checkDuplicateValueExists(amountOptions)
                if duplicate_flag==True:
                    status=0
                    message.append('Duplicate values found in Amount Options Array')

            if not tenureOptions or not isinstance(tenureOptions,list):
                status=0
                message.append('Tenure Options have to be an array')
            if tenureOptions:
                for x in tenureOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Tenure Options has to contain Integers only and cannot be less than 0')
                        break
                duplicate_flag = checkDuplicateValueExists(tenureOptions)
                if duplicate_flag==True:
                    status=0
                    message.append('Duplicate values found in Tenure Options Array')
            if not isinstance(benefitPercentage,int) or benefitPercentage <= 0:
                status=0
                message.append('Benefit Percentage has to be an integer value and cannot be less than 0')
            if not benefitType or benefitType=='':
                status=0
                message.append('Benefit Type cannot be empty')
        except Exception as e:
            return JsonResponse("Something went wrong, Please try again after some time.",safe=False)

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        amountOptions.sort()
        tenureOptions.sort()
        plan=Plan()
        plan.planName=planName
        plan.amountOptions=amountOptions
        plan.tenureOptions=tenureOptions
        plan.benefitPercentage=benefitPercentage
        plan.status=1
        plan.benefitType=benefitType

        try:
            plan.save()
            return JsonResponse("Plan added successfully",safe=False) 
        except:
            return JsonResponse("Failed to Add",safe=False)
    if request.method=='PUT':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)
            planID=data['planID']
            planName=data['planName']
            amountOptions=data['amountOptions']
            tenureOptions=data['tenureOptions']
            benefitPercentage=data['benefitPercentage']
            benefitType=data['benefitType']
            if not planID or not isinstance(planID,int) or planID=='':
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
                duplicate_flag = checkDuplicateValueExists(amountOptions)
                if duplicate_flag==True:
                    status=0
                    message.append('Duplicate values found in Amount Options Array')
            if tenureOptions and not isinstance(tenureOptions,list):
                status=0
                message.append('Tenure Options have to be an array')
            if tenureOptions:
                for x in tenureOptions:
                    if not isinstance(x,int) or x<=0:
                        status=0
                        message.append('Tenure Options has to contain Integers only and cannot be less than 0')
                        break
                duplicate_flag = checkDuplicateValueExists(tenureOptions)
                if duplicate_flag==True:
                    status=0
                    message.append('Duplicate values found in Tenure Options Array')
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
        
        if amountOptions:
           amountOptions=amountOptions.sort() 
        if tenureOptions:
            tenureOptions=tenureOptions.sort()
        plan = Plan.objects.filter(pk=planID,status=1).first()
        if plan:
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
        else:
            return JsonResponse("No Plan Found",safe=False)
    if request.method=='DELETE':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        planID=data['planID']
        if not planID or not isinstance(planID,int) or planID=='':
            status=0
            message.append('Plan ID has to be an integer value and cannot be empty')
        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        plan = Plan.objects.filter(pk=planID).first()
        try:
            if plan:
                plan.status=0
                plan.save()
                return JsonResponse("Plan deleted successfully",safe=False)
            return JsonResponse("Plan doesn't exist",safe=False)  
            
        except Exception as e:
            return JsonResponse(e,safe=False)
def checkDuplicateValueExists(data_array):
    array_len=len(data_array)
    set_len=len(set(data_array))
    if array_len==set_len:
        return False
    return True

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False
@csrf_exempt
def promotionApi(request):
    status=1
    message=[]
    response_data={}
    today = datetime.datetime.now().date()
    if request.method=='GET':
        try:
            promotion = Promotions.objects.filter(status=1)      
            if promotion.exists(): 
                promotion_serializedData = [ {'promotionID': p.promotionID,'user_cap': p.user_cap,'start_date':p.start_date,'end_date':p.end_date} for p in promotion]
                count=len(promotion_serializedData)
        except:
            count = 0
            promotion_serializedData = []
        return JsonResponse({'status':1,'count':count,'data':promotion_serializedData},safe=False)
    if request.method=='POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        promotionID=data['promotionID']
        promotion_start_date=datetime.datetime.strptime(str(data['start_date']),"%Y-%m-%d").date()
        promotion_end_date=datetime.datetime.strptime(str(data['end_date']),"%Y-%m-%d").date()
        user_cap=data['user_cap'] 
        if not promotionID or not isinstance(promotionID,int) or promotionID<=0:
            status=0
            message.append('Promotion ID has to be an integer value and cannot be empty')
        if user_cap ( not isinstance(user_cap,int) or user_cap<=0):
            status=0
            message.append('User Capacity variable has to be an integer value and cannot be less than or equal to zero')
        if ( promotion_start_date and promotion_start_date=='' or promotion_start_date < today):
            status=0
            message.append('Promotion start date cannot be empty ,Promotion start date has to be of date format and cannot be less than current day')
        if ( promotion_end_date or promotion_end_date=='' or promotion_end_date < today):
            status=0
            message.append('Promotion end date cannot be empty ,Promotion end date has to be of date format and cannot be less than current day')
        if promotion_start_date and promotion_end_date and status==1 and promotion_start_date > promotion_end_date:
            status=0
            message.append('Promotion start date cannot be greater than Promotion end date')

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)


        promotion=Promotions.objects.filter(planID_id=planID,start_date__lte=promotion_start_date , end_date__gte=promotion_start_date,status=1) | Promotions.objects.filter(planID_id=planID,start_date__lte=promotion_end_date , end_date__gte=promotion_end_date,status=1)
        if promotion.exists():
            status=0
            message.append('A promotion already exists for this plan ID, please delete this plan or change start date of Promotion')

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        new_promotion=Promotions()
        new_promotion.planID_id=planID
        new_promotion.user_cap=user_cap
        new_promotion.status=1
        new_promotion.start_date=promotion_start_date
        new_promotion.end_date=promotion_end_date

        try:
            new_promotion.save()
            return JsonResponse("Promotion added successfully",safe=False) 
        except:
            return JsonResponse("Failed to add Promotion",safe=False)
    if request.method=='PUT':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        planID=data['planID']
        promotionID=data['promotionID']
        promotion_start_date=datetime.datetime.strptime(str(data['start_date']),"%Y-%m-%d").date()
        promotion_end_date=datetime.datetime.strptime(str(data['end_date']),"%Y-%m-%d").date()
        user_cap=data['user_cap'] 
        if not promotionID or not isinstance(promotionID,int) or promotionID<=0:
            status=0
            message.append('Promotion ID has to be an integer value and cannot be empty')
        if not user_cap or not isinstance(user_cap,int) or user_cap<=0:
            status=0
            message.append('User Capacity variable has to be an integer value and cannot be less than or equal to zero')
        if not promotion_start_date or promotion_start_date=='' or promotion_start_date < today:
            status=0
            message.append('Promotion start date cannot be empty ,Promotion start date has to be of date format and cannot be less than current day')
        if not promotion_end_date or promotion_end_date=='' or promotion_end_date < today:
            status=0
            message.append('Promotion end date cannot be empty ,Promotion end date has to be of date format and cannot be less than current day')
        if promotion_start_date and promotion_end_date and status==1 and promotion_start_date > promotion_end_date:
            status=0
            message.append('Promotion start date cannot be greater than Promotion end date')

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        promotion_info = Promotions.objects.filter(pk=promotionID,status=1).first()
        if promotion_info:
            planID = promotion_info.planID_id

            if promotion_start_date and status==1:
                promotion = Promotions.objects.filter(status=1,planID_id=planID,start_date__lte=promotion_start_date , end_date__gte=promotion_start_date).exclude(promotionID=promotionID)
                if promotion.exists():
                    status=0
                    message.append('A promotion already exists for this plan ID, please delete this plan or change start date of Promotion')
                else:
                    promotion_info.start_date=promotion_start_date
            if promotion_end_date and status==1:
                promotion = Promotions.objects.filter(status=1,planID_id=planID,start_date__lte=promotion_end_date , end_date__gte=promotion_end_date).exclude(promotionID=promotionID)
                if promotion.exists():
                    status=0
                    message.append('A promotion already exists for this plan ID, please delete this plan or change end date of Promotion')
                else:
                    promotion_info.end_date=promotion_end_date
            if user_cap and status==1:
                promotion_info.user_cap=user_cap
        else:
            status=0
            message.append('No Promotion present with this promotionID')

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        try:
            promotion_info.save()
            return JsonResponse("Promotion updated successfully",safe=False) 
        except:
            return JsonResponse("Failed to update Promotion",safe=False)
    if request.method=='DELETE':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        promotionID=data['promotionID']
        if not promotionID or not isinstance(promotionID,int) or promotionID=='':
            status=0
            message.append('promotionID has to be an integer value and cannot be empty')
        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        promotion = Promotions.objects.filter(pk=promotionID).first()
        try:
            if promotion:
                promotion.status=0
                promotion.save()
                return JsonResponse("Promotion deleted successfully",safe=False)
            return JsonResponse("Promotion doesn't exist",safe=False)  
            
        except Exception as e:
            return JsonResponse(e,safe=False)
        
@csrf_exempt
def customerGoalsApi(request):
    status=1
    message=[]
    response_data={}
    if request.method=='GET':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        userID=data['userID']
        if userID and ( not isinstance(userID,int) or userID<=0 ):
            status=0
            message.append('UserID has to in Integer format')
        
        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)

        if userID:
            customergoals = CustomerGoals.objects.filter(userID=userID,status=1)

            customergoals = CustomerGoals.objects.raw("select userID, tortoiseapi_customergoals.selectedAmount,tortoiseapi_customergoals.selectedTenure , tortoiseapi_customergoals.depositedAmount,tortoiseapi_customergoals.planID_id , tortoiseapi_plan.planName from tortoiseapi_customergoals left join tortoiseapi_plan on tortoiseapi_customergoals.planID_id = tortoiseapi_plan.planID where tortoiseapi_customergoals.status = 1",userID=userID)
        else:
            customergoals = CustomerGoals.objects.raw("select userID, tortoiseapi_customergoals.selectedAmount,tortoiseapi_customergoals.selectedTenure , tortoiseapi_customergoals.depositedAmount,tortoiseapi_customergoals.planID_id , tortoiseapi_plan.planName from tortoiseapi_customergoals left join tortoiseapi_plan on tortoiseapi_customergoals.planID_id = tortoiseapi_plan.planID where tortoiseapi_customergoals.status = 1")
        
        try:     
            if customergoals.exists(): 
                customergoals_serializedData = [ {'userID': p.userID,'selectedAmount': p.selectedAmount,'selectedTenure':p.selectedTenure,'depositedAmount':p.depositedAmount,'benefitPercentage':p.benefitPercentage,'planName':p.planName} for p in customergoals]
                count=len(customergoals_serializedData)
        except:
            count = 0
            customergoals_serializedData = []
        return JsonResponse({'status':1,'count':count,'data':customergoals_serializedData},safe=False)
    if request.methos=='POST':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        planID=data['planID']
        promotionID=data['promotionID']
        tenureOptions=data['tenureOptions']
        selectedAmount=data['selectedAmount']
        selectedTenure=data['selectedTenure']
        depositedAmount=data['depositedAmount']
        benefitPercentage=data['benefitPercentage']

        if not planID or planID=='' or not isinstance(planID,int):
            status=0
            message.append('Plan ID has to be an integer value and cannot be empty')
        if not promotionID or promotionID=='' or not isinstance(promotionID,int):
            status=0
            message.append('promotionID has to be an integer value and cannot be empty')
        if not tenureOptions or tenureOptions=='' or not isinstance(tenureOptions,int) or tenureOptions <= 0:
            status=0
            message.append('tenureOptions has to be an integer value and cannot be empty')
        if not selectedAmount or selectedAmount=='' or not isinstance(selectedAmount,int) or selectedAmount <= 0:
            status=0
            message.append('selectedAmount has to be an integer value and cannot be empty')
        if not selectedTenure or selectedTenure=='' or not isinstance(selectedTenure,int) or selectedTenure<=0:
            status=0
            message.append('selectedTenure has to be an integer value and cannot be empty')
        if not depositedAmount or depositedAmount=='' or not isinstance(depositedAmount,int) or depositedAmount<=0:
            status=0
            message.append('depositedAmount has to be an integer value and cannot be empty')
        if not benefitPercentage or benefitPercentage=='' or not isinstance(benefitPercentage,int) or benefitPercentage<=0:
            status=0
            message.append('benefitPercentage has to be an integer value and cannot be empty')

        if status==0:
            response_data['status']=status
            response_data['message']=message
            return JsonResponse(response_data,safe=False)
        
        customergoals = CustomerGoals()
        customergoals.userID=userID
        customergoals.planID_id=planID
        customergoals.promotionID_id=promotionID
        customergoals.selectedTenure=selectedTenure
        customergoals.selectedAmount=selectedAmount
        customergoals.depositedAmount=depositedAmount
        customergoals.benefitPercentage=benefitPercentage
        customergoals.status=1
        customergoals.created_at=datetime.now()
        customergoals.updated_at=datetime.now()

        try:
            customergoals.save()
            return JsonResponse("Customer Goals created successfully",safe=False)
        except:
            return JsonResponse("Customer Goals creation failed",safe=False)

    if request.method=='DELETE':
        body = request.body.decode('utf-8')
        data = json.loads(body)
        customerGoalID=data['customerGoalID']

        if not customerGoalID or customerGoalID=='' or not isinstance(customerGoalID,int):
            status=0
            message.append('customerGoalID has to be an integer value and cannot be empty')
        
        customergoals=CustomerGoals.objects.filter(customerGoalID=customerGoalID,status=1).first()
        if customergoals:
            try:
                customergoals.status=0
                customergoals.save()
                return JsonResponse("Customer Goals deleted successfully",safe=False)
            except:
                return JsonResponse("Customer Goals deletion failed",safe=False)
        else:
            return JsonResponse("Customer Goals not found",safe=False)
        
        








