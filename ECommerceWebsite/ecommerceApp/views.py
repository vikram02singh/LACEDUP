import json
from ecommerceApp import keys
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render ,redirect, HttpResponse
from ecommerceApp.models import Contact,Orders, OrderUpdate,Product
from math import ceil
from django.http import JsonResponse
import razorpay
import json

# from razorpay import Checksum

# Create your views here.

def index(request):
    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={item['category']for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nSlides),nSlides])

    params={'allProds':allProds}

    return render(request,"index.html",params)

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        desc=request.POST.get('desc')
        phonenbr=request.POST.get('phonenbr')
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=phonenbr)
        myquery.save()
        messages.info(request,"Our team will contact you soon.")
        return render(request,"contact.html")
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")
def profile(request):
    return render(request,"profile.html")
def privacy(request):
    return render(request,"privacy.html")
def terms(request):
    return render(request,"terms.html")

def signin(request):
    return render(request,"signin.html")

def blog(request):
    return render(request,"blog.html")
def my_order(request):
    return render(request,"my_order.html")


client = razorpay.Client(auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login/')
        
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount_str = request.POST.get('amt', '')
        try:
            amount = int(amount_str) * 100  # amount in paise for razorpay
            if amount < 100:
                messages.error(request, "Minimum amount is ₹1")
                return redirect('checkout')  # Please adjust URL name accordingly
        except Exception:
            messages.error(request, "Invalid amount")
            return redirect('checkout')

        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        phone = request.POST.get('phone', '')

        order = Orders(
            items_json=items_json,
            name=name,
            email=email,
            amount=amount / 100,  # store amount in rupees
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            phone=phone
        )
        order.save()
        # Create razorpay order
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Save razorpay order id in your order model
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        update = OrderUpdate(order_id=order, update_desc="Order has been placed")
        update.save()

        context = {
            'order_id': razorpay_order['id'],
            'razorpay_key': keys.RAZORPAY_KEY_ID,
            'amount': amount,
            'order_model_id': order.order_id,
            'user': request.user,
        }
        print("RAZORPAY_KEY_ID from keys.py:", keys.RAZORPAY_KEY_ID)

        return render(request, "payment.html", context)
    context = {
        'razorpay_key': keys.RAZORPAY_KEY_ID,
        'user': request.user,
    }
    return render(request, "checkout.html", context)
    
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        # Process payment success details here
        # You can get payment id, order id etc. from POST data
        # You should verify payment signature with Razorpay if required

        # Example minimal confirmation:
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        try:
            order = Orders.objects.get(razorpay_order_id=order_id)
            order.payment_id = payment_id
            order.status = "PAID"
            order.save()

            update = OrderUpdate(order_id=order.order_id, update_desc="Payment successful")
            update.save()

            messages.success(request, "Payment successful! Your order is confirmed.")
            return redirect('my_order')  # Or wherever appropriate
        except Orders.DoesNotExist:
            return HttpResponse("Order not found", status=404)

    return HttpResponse("Invalid request", status=400)


# def checkout(request):
#     if not request.user.is_authenticated:
#         messages.warning(request, "Login & Try Again")
#         return redirect('/auth/login/')
        
#     if request.method == "POST":
#         items_json = request.POST.get('itemsJson', '')
#         name = request.POST.get('name', '')
#         # amount = request.POST.get('amt', '')
#         amount = request.POST.get('amount')
#         if amount:
#             amount = int(amount)
#         else:
#             amount = 0  # or raise a validation error

#         email = request.POST.get('email', '')
#         address1 = request.POST.get('address1', '')
#         address2 = request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         zip_code = request.POST.get('zip_code', '')
#         phone = request.POST.get('phone', '')
#         Order=Orders(
#             items_json=json,
#             name=name,email=email,amount=amount, address1=address1,address2=address2, city=city,state=state,phone=phone 
#         )
#         print(amount)
#         Order.save()       
#         update = OrderUpdate(order_id=Order.order_id, update_desc="Order has been placed")
#         update.save()
#         thank = True
        

#         # PAYMENT INTEGRATION
#         id = Order.order_id
#         oid = str(id) + "shopcycart"
#         param_dict = {
#             'MID': keys.MID, 
#             'ORDER_ID': oid,
#             'TXN_AMOUNT': str(amount),
#             'CUST_ID': email,
#             'INDUSTRY_TYPE_ID': 'Retail',
#             'WEBSITE': 'WEBSTAGING',
#             'CHANNEL_ID': 'WEB',
#             'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
#             }

#         param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, keys.MKEY)  # type: ignore
#         return render(request, 'paytm.html', {'param_dict': param_dict})

#     return render(request,"checkout.html")

# @csrf_exempt # type: ignore
# def handlerequest(request):
#     # paytm will send you post request here
#     form = request.POST
#     response_dict = {}
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i]

#     verify = checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum) # type: ignore
#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             print('order successful')
#         else:
#             print('order was not successful')

#     a = response_dict['ORDERID']
#     b = response_dict['TXNAMOUNT']
#     rid = a.replace("shopycart", "")

#     print(rid)
#     filter2 = Orders.objects.filter(order_id=rid)
#     print(filter2)
#     print(a, b)
#     for post1 in filter2:
#         post1.oid = a
#         post1.amountpaid = b

#         post1.paymentstatus = "PAID"
#         post1.save()
#         print("run aged function")
#     else:
#         print("order was not successful because:", response_dict['RESPMSG'])

#     return render(request, 'paymentstatus.html', {'response': response_dict})


# RAZORPAY_KEY_ID = 'rzp_test_XOsIbfJ9iB1Og7'
# RAZORPAY_KEY_SECRET = 'PEYKiqe4deGZszupCTAzB0a4'

# client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# def checkout(request):
#         raw_amount=0
#         # amount = int(request.POST.get("amount")) * 100  #Convert to paise
#         if request.method == "POST":
#               raw_amount = request.POST.get("amt", "0")
#               print(f"Raw amount from POST: {raw_amount}")  # Debug
#         try:
#                  amount = int(raw_amount) * 100
#                  if amount < 100:
#                   return HttpResponse("Amount must be at least ₹1", status=400)
#         except ValueError:
#                  return HttpResponse("Invalid amount received", status=400)



#         razorpay_order = client.order.create(dict(raw_amount=raw_amount, currency="INR", payment_capture='1'))
#         order = Orders.objects.create(
#             order_id=razorpay_order['id'],
#             amount=amount,
#             # status='CREATED'
           
#         )
#         return render(request, "payment.html", {
#             'order': order,
#             'razorpay_key': RAZORPAY_KEY_ID
#         })
    
   
# @csrf_exempt

# def payment_success(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         order_id = data.get("order_id")
#         payment_id = data.get("payment_id")

#         try:
#             order = Orders.objects.get(order_id=order_id)
#             order.payment_id = payment_id
#             order.status = "PAID"
#             order.save()
#             return JsonResponse({"message": "Payment verified successfully!"})
#         except Orders.DoesNotExist:
#             return JsonResponse({"error": "Order not found"}, status=404)
