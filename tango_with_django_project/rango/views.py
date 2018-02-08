from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

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

@login_required
def add_category(request):
    form = CategoryForm()

    #An HTTP Post?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Provided w/ a valid form?
        if form.is_valid():
            #save new cat. to DB
            category = form.save(commit = True)
            form.save(category, category.slug)
            #now that it's saved, give confirm. message
            #Since cat. added is on index, redirect to index page
            return index(request)
        else:
            #supplied form has errors, print to terminal
            print(form.errors)

    # will handle bad form, new form, or no form cases.
    # render form w/ any error messages
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # boolean to tel the template whether registration was successful.
    # set to false to start, code changes to true when successful
    registered = False

    # if it's HTTP POST, we want to proccess form data
    if request.method == 'POST':
        # attempt to grab info from raw form info
        # use both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save form data to database
            user = user_form.save()

            # now hash the password with the set_password method
            # once hashed, update user object
            user.set_password(user.password)
            user.save()

            # now sort out the UserProfile instance. Since we set user
            # attributes ourselves, we set commit=false. This delays saving
            # the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # did user provide profile pic? If so, get it from input form
            # and put it in the UserProfile models
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # now save UserProfile model instance
                profile.save()

            # update variables to indicate template reg. was successful
                registered = True
        else:
            # invalid form/s - mistake or something else?
            # print problem to the terminal for user
            print(user_form.errors, profile_form.errors)
    else:
        # not HTTP POST, so render the form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    # if request is HTTP POST, try and pull out relevant info
    if request.method == 'POST':
        # gather user & pass from login form.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use Django to attempt to see if user/pass is valid
        user = authenticate(username=username, password=password)

        # if a User object, details are correct.
        # if none, no user with matching credentials was found
        if user:
            # is the acct active?
            if user.is_active:
                # if acct is valid and active, log user in, send to homepage
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # inactive acct, no logging in
                return HttpResponse("Your Rango account is disabled.")
        else:
            # bad login details, can't log in
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # the request isn't HTTP POST, so display login form
    else:
        # No context variables to pass to template, gives blank directory object
         return render(request, 'rango/login.html', {})



@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    # since we know user is logged in, can offer to log out
    logout(request)
    # take user to homepage
    return HttpResponseRedirect(reverse('index'))
