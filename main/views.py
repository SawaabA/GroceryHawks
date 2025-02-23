from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .text_classification import search_database
from django.http import JsonResponse
import json



from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
import logging


from django.core.paginator import Paginator

import pandas as pd
import os
import random
from django.shortcuts import render

def search_items(request, keyword):
    try:
        result = search_database(keyword)
        return JsonResponse({"result": result})
    except json.JSONDecodeError as err:
        return JsonResponse({"error": str(err)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


def home(request):
    return render(request, "main/home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    login_form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        # Process login submission
        if login_form.is_valid():
            user = login_form.get_user()
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(
                    request,
                    "Login attempt unsuccessful. Please re-enter your username and password.",
                )
    return render(request, "accounts/login.html", {"login_form": login_form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    register_form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        # Process registration submission
        if register_form.is_valid():
            register_form.save()
            messages.success(request, "Your account has been created! Please log in.")
            return redirect("login")
    return render(request, "accounts/register.html", {"register_form": register_form})


def dashboard(request):
    return render(request, "main/dashboard.html")


def grocery_search(request):
    return render(request, "main/grocerysearch.html")





# Define the CSV file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "datasets/globaldataset.csv")

def get_lowest_price_products():
    try:
        # Load CSV file
        df = pd.read_csv(CSV_FILE_PATH)

        # Ensure numerical values for price columns
        price_columns = ["Walmart", "Zehrs", "Freshco", "Food Basics", "Canadian Superstore", "Farahs", "No Frills"]
        df[price_columns] = df[price_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

        # Find the lowest price and corresponding store(s)
        df["lowest_price"] = df[price_columns].min(axis=1)
        df["cheapest_stores"] = df.apply(lambda row: [store for store in price_columns if row[store] == row["lowest_price"]], axis=1)

        # Sort by lowest price and get top 50 cheapest products
        df_sorted = df.sort_values(by="lowest_price").head(50)

        # Select 4 random products
        random_products = df_sorted.sample(n=4).to_dict(orient="records")

        return random_products

    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

def dashboard(request):
    # Get random lowest-priced products
    products = get_lowest_price_products()

    return render(request, "main/dashboard.html", {"products": products})


# -------------------------------
def all_groceries(request):
    try:
        # Load dataset
        df = pd.read_csv(CSV_FILE_PATH)

        # Remove exact duplicate titles (optional)
        df.drop_duplicates(subset=["title"], keep="first", inplace=True)

        # Ensure numerical values
        price_columns = ["Walmart", "Zehrs", "Freshco", "Food Basics", 
                         "Canadian Superstore", "Farahs", "No Frills"]
        df[price_columns] = df[price_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

        # Handle search query
        search_query = request.GET.get('q', '')
        if search_query:
            df = df[df['title'].str.contains(search_query, case=False, na=False)]

        # Calculate lowest price
        df["lowest_price"] = df[price_columns].min(axis=1)

        # Create a dictionary of store prices
        df["all_stores"] = df.apply(
            lambda row: {store: row[store] for store in price_columns if row[store] > 0},
            axis=1
        )

        # Fill missing image URLs
        df["Image"] = df["Image"].fillna("https://via.placeholder.com/150")

        # Convert to list of dictionaries
        groceries = df.to_dict(orient="records")

        # Implement Pagination (20 items per page)
        paginator = Paginator(groceries, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Render the template
        return render(request, "main/all_groceries.html", {
            "page_obj": page_obj,
            "search_query": search_query
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

    # -------------------
client = OpenAI(api_key="")
logger = logging.getLogger(__name__)

@csrf_exempt
def top_deals(request):
    chatbot_response = None  

client = OpenAI(api_key="")
logger = logging.getLogger(__name__)

@csrf_exempt
def top_deals(request):
    chatbot_response = None  

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")

            if not user_input:
                return JsonResponse({"error": "No input received"}, status=400)

            # Send request to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "You are a grocery deals assistant. Provide concise answers. Also, for every response say "
                        "I AM THE HAWK! Bringing you the best deals from the sky no matter what! Scan the skies for the "
                        "latest grocery deals! 🦅💨\n\n"
                        "From Walmart:\n\n"
                        "Save 50% on Clementines (4lb) for $3.44 🍊\n"
                        "Fresh Market Salad Greens $3.97 🥗\n"
                        "Johnsonville Breakfast Sausages $3.97 🌭\n"
                        "Maxwell House Coffee $4.97 ☕\n"
                        "Barilla Pasta $1.97 🍝\n"
                        "Cashmere 30-Pack Toilet Paper $15.97 🧻\n\n"
                        "From FreshCo:\n\n"
                        "Maple Leaf Chicken Breast 2 for $24 🍗\n"
                        "Raspberries $1.99 🍓\n"
                        "Activia Yogurt 3 for $11 🥄\n\n"
                        "From Zehrs:\n\n"
                        "Lean Ground Beef $4.97/lb 🥩\n"
                        "Salmon Fillets $9.99/lb 🐟\n"
                        "Huggies Diapers $34.99 🍼"
                    )},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.7,
                max_tokens=150
            )

            chatbot_response = response.choices[0].message.content.strip()

            return JsonResponse({"response": chatbot_response})

        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    # For GET requests, render the top_deals template.
    return render(request, "main/top_deals.html", {"chatbot_response": chatbot_response})
