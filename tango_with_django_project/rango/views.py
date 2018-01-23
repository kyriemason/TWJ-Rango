from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

def index(request):
    # Query DB for list of ALL categories currently stored.
    # Order cats by no. likes in descending Order
    # Retrieve the top 5 only - or all if less than 5
    # Place list in context_dict dictionary
    # that's passed to template engine
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories' : category_list}


    # What's going on: this returns a rendered response to send to client.  We make use
    # of the shortcut function to make life easier. Note that 1st parameter is template we want to use
    return render(request, 'rango/index.html', context_dict)

def about(request):
    context_dict = {'aboutmessage' : "here is the about page"}

    # return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/'>View Index</a>")

    return render(request, 'rango/about.html', context=context_dict)
