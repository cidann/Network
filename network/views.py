from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import User,Post
import json

def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def create(request):
    if(request.method=='POST'):
        user=request.user
        content=request.body.decode()
        Post(user=user,content=content).save()
        return JsonResponse({"message": "Post recorded."}, status=200)
    else:
        return JsonResponse({'error':'POST request required'},status=400)

def posts(request,filter):
    if(request.method=='GET'):
        data=[]
        if(filter=='all'):
            for i in Post.objects.all():
                data.append({
                    'id':i.id,
                    'user':i.user.username,
                    'content':i.content,
                    'time':i.time,
                    'like':i.like
                })
        elif(filter=='following'):
            pass
        return JsonResponse(data,status=200,safe=False)
    else:
        return JsonResponse({'error':'GET request required'},status=400)