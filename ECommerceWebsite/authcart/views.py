from django.contrib import messages
from django.shortcuts import render ,redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

# from django.core.mail import send_mail
# from django.core.mail import EmailMessage
# from django.conf import settings
# # send_mail(
#     "Subject here",
#     "Here is the message.",
#     "from@example.com",
#     ["to@example.com"],
#     fail_silently=False,
# )



def signup(request):
    if request.method=="POST":
       
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        if pass1 != pass2:
             messages.warning(request,"Password doesn't match!")
             return render(request,'signup.html')
        try:
             if User.objects.get(username=email):
                   messages.warning(request,"User already Registered!")
                   return render(request,"signup.html")
        except Exception as identifier:
             pass
        user=User.objects.create_user(email,email,pass1)
        user.save()
        # return HttpResponse("User Created ")
    return render(request,'signup.html')   
def handle_login(request):
    if request.method=="POST":
         
         username=request.POST['email']
         userpassword=request.POST['pass1']
         myuser=authenticate(username=username,password=userpassword)
         
         if myuser is not None:
               login(request, myuser)
            #    messages.success(request,"Login Success")
               return redirect('/')
         else:
                messages.warning(request,"Invalid Credentials")
                return redirect('/auth/login')
    return render(request,"login.html")

def handle_logout(request):
    logout(request)
    # messages.info(request,"Loged Out Successfully")
    return redirect('/auth/login')