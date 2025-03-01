from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def nfactorial(request):
    return render(request, 'nfactorial/nfactorial.html')

def add_numbers(request, one, two):
    result = one + two
    return HttpResponse(f'{one} + {two} = {result}')

def upper(request, text):
    return HttpResponse(text.upper())

def palindrome(request, text):
    if text == text[::-1]:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def calculator(request, one, operand, two):
    if operand == 'add':
        return HttpResponse(f'{one} + {two} = {one + two}')
    elif operand == 'sub':
        return HttpResponse(f'{one} - {two} = {one - two}')
    elif operand == 'mult':
        return HttpResponse(f'{one} * {two} = {one * two}')
    elif operand == 'div' and two != 0:
        return HttpResponse(f'{one} / {two} = {one / two}')
    else:
        return HttpResponse('wrong data')