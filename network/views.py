from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import User,Post
import json
import re

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

def posts(request):
    if(request.method=='GET'):
        filter=request.GET.get('filter','all')
        def apiformat(data):
            api=[]
            for i in data:
                api.append({
                    'id': i.id,
                    'user': i.user.username,
                    'content': i.content,
                    'time': i.time.strftime('%B %d, %Y, %I:%M %p'),
                    'like': i.like
                })
            return api
        if(filter=='all'):
            api=apiformat(Post.objects.order_by('-time'))
        elif(filter=='following'):
            api=apiformat(Post.objects.filter(user__in=request.user.following))
        elif(filter.startswith('person-')):
            person=re.search('person-(.+)',filter)
            api=apiformat(Post.objects.filter(user=person))
        return JsonResponse(api,status=200,safe=False)
    else:
        return JsonResponse({'error':'GET request required'},status=400)

def profile(request,user):
    try:
        return render(request,'network/profile.html',{
            'profile':User.objects.get(username=user)
        })
    except:
        return HttpResponse('The user does not exist')

def followers(request,user):
    if(request.method=='GET'):
        return render(request,'network/followers.html',{
            'profile':user,
            'followers':User.objects.get(username=user).followers.all()
        })
    elif(request.method=='PUT'):
        user=User.objects.get(username=user)
        if(request.user in user.followers.all()):
            user.followers.remove(request.user)
        else:
            user.followers.add(request.user)
        return JsonResponse({'sucess':'True'},status=200)