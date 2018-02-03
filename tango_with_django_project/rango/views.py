from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
    # Query DB for list of ALL categories currently stored.
    # Order cats by no. likes in descending Order
    # Retrieve the top 5 only - or all if less than 5
    # Place list in context_dict dictionary
    # that's passed to template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories' : category_list, 'pages': page_list}


    # What's going on: this returns a rendered response to send to client.  We make use
    # of the shortcut function to make life easier. Note that 1st parameter is template we want to use
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    context_dict = {'aboutmessage' : "here is the about page"}

    # return HttpResponse("Rango says here is the about page. <br/> <a href='/rango/'>View Index</a>")
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    #create context dictionary which we can pass to template rendering engine
    context_dict = {}

    try:
        #can you find a cat. name slug with the given name?
        #if you cant, the .get() method rases a DoesNotExist exception.
        #So the .get() method returns one model instance or rases exception
        category = Category.objects.get(slug=category_name_slug)

        #retrieve all associated pages.
        #Note that filter() will return list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        #Add our results list to the template context under name pages
        context_dict['pages'] = pages
        #Also add the cat. object from the DB to the context dictionary
        #You use this in the template to verify that the cat. exits
        context_dict['category'] = category
    except Category.DoesNotExist:
        #We get here if specified cat. isn't found, don't do anything
        #template will display 'no cat.' message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    #Go render the response & return it to the client
    return render(request, 'rango/category.html', context_dict)
