from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
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
    elif(request.method=='PATCH'):
        body=json.loads(request.body)
        post=Post.objects.get(id=body['id'])
        change=body['content']
        post.content=change
        post.save()
        return JsonResponse({'message':'Post updated'})
    else:
        return JsonResponse({'error':'POST or PATCH request required'},status=400)

def posts(request):
    if(request.method=='GET'):
        if(int(request.GET.get('pagenum',0))<1):
            return JsonResponse({'error':'page has to be 1 or greater'},status=400)
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
            pages=Paginator(api,10)
            page=pages.page(int(request.GET['pagenum']))
            return {'previous':page.has_previous(),'next':page.has_next(),'page':page.object_list}
        if(filter=='all'):
            api=apiformat(Post.objects.order_by('-time'))
        elif(filter=='following'):
            api=apiformat(Post.objects.filter(user__in=request.user.following.all()).order_by('-time'))
        elif(filter.startswith('person-')):
            person=re.findall('person-(.+)',filter)[0]
            user=User.objects.get(username=person)
            api=apiformat(Post.objects.filter(user=user).order_by('-time'))
        return JsonResponse(api,status=200)
    else:
        return JsonResponse({'error':'GET request required'},status=400)

def profile(request,user):

        return render(request,'network/profile.html',{
            'profile':User.objects.get(username=user)
        })


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
        return JsonResponse({'count':user.followers.count()},status=200)
    else:
        return JsonResponse({'error':'GET or PUT method required'},status=400)

def followed(request,user):
    if(request.method=='GET'):
        return render(request,'network/followed.html',{
            'profile':user,
            'following':User.objects.get(username=user).following.all()
    })
    else:
        return JsonResponse({'error':'use followers url to follow'},status=400)

def like(request):
    if(request.method=='GET'):
        post_id=request.GET['id']
        likedlist=[]
        for i in Post.objects.get(id=post_id).likers.values_list('username'):
            likedlist.append(i[0])
        return JsonResponse({
            'liked':likedlist
        },status=200)
    elif(request.method=='POST'):
        post_id = request.GET['id']
        post=Post.objects.get(id=post_id)
        user=request.user
        if(user in post.likers.all()):
            post.likers.remove(user)
            post.like-=1
            post.save()
            status='unliked'
        else:
            post.likers.add(user)
            post.like+=1
            post.save()
            status='liked'
        post.like,likecount=[post.likers.count()]*2
        return JsonResponse({'status':status,'likecount':likecount},status=200)
    else:
        return JsonResponse({'error':'GET or POST method required'},status=400)

def following(request):
    return render(request,'network/following.html')