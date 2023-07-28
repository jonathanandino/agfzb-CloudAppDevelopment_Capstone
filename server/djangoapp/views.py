from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)
        
# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('/djangoapp/')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('/djangoapp')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    ctx = {}
    if request.method == "GET":
        url = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudant.com/dealerships"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name

        ctx['dealerships'] = dealerships
        return render(request, 'djangoappSCD/index.html', ctx)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    ctx = {}
    url = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudant.com/reviews/_all_docs"
    # Get dealers from the URL
    reviews = get_dealer_reviews_from_cf(url,dealer_id)
    ctx['reviews'] = reviews
    ctx['dealer'] = dealer_id
    # Concat all dealer's short name
    dealer_details = ' '.join([dealer.review for dealer in reviews])
    # Return a list of dealer short name
    return render(request, 'djangoappSCD/dealer_details.html', ctx)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):

    if request.method == "POST":
        if request.user.is_authenticated:
            url = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudant.com/reviews"
            url2 = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudant.com/dealerships"

            car = CarModel.objects.get(id=request.POST['car'])
            dealer = get_dealer_by_id(url2, dealer_id)

            if request.POST['purchasecheck'] == "on":
                purchase = True
            else:
                purchase = False

            payload = {
                'review': {
                    "car_make": car.model_id.name,
                    "car_model": car.name,
                    "car_year": car.year.year,
                    "dealership": dealer_id,
                    "name": dealer.full_name,
                    "purchase": purchase,
                    "purchase_date": request.POST['purchasedate'],
                    "review": request.POST['content']
                }
            }

            json_result = post_request(url, payload)
            review = json_result

            ctx = {}
            ctx['dealer'] = dealer
            ctx['cars'] = list(CarModel.objects.all())
            ctx['created'] = True
            return render(request, 'djangoappSCD/add_review.html', ctx)

        else:
            raise PermissionDenied("Only auth users can post.")
    else:
        ctx = {}
        url = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudant.com/dealerships"
        ctx['dealer'] = get_dealer_by_id(url, dealer_id)
        ctx['cars'] = list(CarModel.objects.all())
        print(ctx['cars'])
        return render(request, 'djangoappSCD/add_review.html', ctx)