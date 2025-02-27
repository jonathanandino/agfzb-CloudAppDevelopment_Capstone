import requests
import json
# import related models here
from djangoapp.models import CarDealer, DealerReview

from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))

    try:
        # no authentication GET
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    else:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, json=json_payload, headers={'Content-Type': 'application/json'},
                                 params=kwargs)
    except:
        print("Network exception occurred on POST request")
    else:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url,dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["rows"]
        # For each dealer object
        for review in reviews:
            sentiment = ""
            review_obj = DealerReview(dealership=review["dealership"],name=review["name"],
                                      purchase=review["purchase"],review=review["review"],
                                      purchase_date=review["purchase_date"],car_make=review["car_make"],
                                      car_model=review["car_model"],car_year=review["car_year"],
                                      sentiment=sentiment)
            results.append(review_obj)
    return results

def get_dealer_by_id(url, dealerId, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        # Get its content in `doc` object
        dealer_doc = dealers[0]
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                               id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                               short_name=dealer_doc["short_name"],
                               st=dealer_doc["st"], zip=dealer_doc["zip"])

    return dealer_obj
    
def get_dealers_by_state(url, state, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,state=state)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_reviews_from_cf(url,dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result
        
        # For each dealer object
        for review in reviews:
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA______", review["doc"], "______________________________________________")
            rev = review["doc"]
            carMake = ""
            purchaseDate = ""
            carModel = ""
            carYear = ""
            sentiment = "positive"


            if len(rev) == 11:
                carMake= review["doc"]["car_make"]
                purchaseDate =review["doc"]["purchase_date"]
                carModel = review["doc"]["car_model"]
                carYear= review["doc"]["car_year"]

            review_obj = DealerReview(dealership=review["doc"]["dealership"],name=review["doc"]["name"],
                                      purchase=review["doc"]["purchase"],review=review["doc"]["review"],
                                      purchase_date=purchaseDate, car_make=carMake,
                                      car_model=carModel,car_year=carYear,
                                      sentiment=sentiment, id=review["doc"]["id"])
            results.append(review_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(dealer_review):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    apikey = "uBgZvwi9DoLUKM_EPNXgw3-w5TuCWn5_yNQwSSW_X33g"
    url = "https://9d5eb47c-7f0d-4761-b898-39c4ab69ec9e-bluemix.cloudantnosqldb.appdomain.cloud"
    
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=dealer_review,
        language='en',
        features=Features(sentiment=SentimentOptions(targets=[dealer_review]))
    ).get_result()

    print(json.dumps(response, indent=2))
    
    return response["sentiment"]["document"]["label"]



