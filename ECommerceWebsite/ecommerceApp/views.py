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

