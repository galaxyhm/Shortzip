# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import (
                                    require_http_methods, 
                                    require_safe, 
                                    require_POST
                                )
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.contrib import auth
from .forms import UserForm

User = get_user_model()

# Create your views here.
@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return HttpResponseBadRequest('이미 로그인 하였습니다.')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            print('폼요청 성공')
            user = form.save()
            print('signup 유효성 검사 통과 및 form 저장')
            auth_login(request, user)
            print('signup 모든 과정 완료')
            return redirect('board:index')
    else:
        form = UserForm()
    context = {'form':form}
    return render(request, 'accounts/signup.html', context)


@require_http_methods(['GET', 'POST'])
def login(request):
    print('시작')
    if request.user.is_authenticated:
        return HttpResponseBadRequest('이미 로그인 하였습니다.')

    if request.method == "POST":
        print('AuthenticationForm 생성 전')
        form = AuthenticationForm(request, request.POST)
        print('AuthenticationForm 생성됨')
        if form.is_valid():
            print('form 유효성 검사 통과')
            user = form.get_user()
            auth_login(request, user)
            return redirect('board:index')
        else:
            print('form 유효성 검사 막힘')
    else:
        form = AuthenticationForm()
    context = {'form' : form}
    print('form context 생성 및 전송 직전')
    return render(request, 'accounts/login.html', context)
    
