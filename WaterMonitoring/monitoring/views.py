from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from page.pages1 import fetch_data, calculate_charges
from datetime import datetime
import pytz
import requests

def home(request):
    return render(request, 'home.html')  

def real_time(request):
    data = fetch_data()
    temp = loader.get_template('real_time.html')
    flow_rate_graph_url = "https://thingspeak.com/channels/2796086/charts/1?bgcolor=%23ffffff&color=%231980FE&dynamic=true&results=60&type=line"
    total_water_graph_url = "https://thingspeak.com/channels/2796086/charts/2?bgcolor=%23ffffff&color=%2327AE60&dynamic=true&results=60&type=line"
    context = {
        'data': data[0],
        'flow_rate_graph_url': flow_rate_graph_url,
        'total_water_graph_url': total_water_graph_url,
        'flag': data[1]
    }
    return HttpResponse(temp.render(context, request))

def about_proj(request):
    return render(request, 'about_project.html')

def analysis_bill(request):
    # ThingSpeak API URL and parameters
    THINGSPEAK_API_URL = "https://api.thingspeak.com/channels/2796086/feeds.json"
    API_KEY = "00GQUMW1ES25ZBE5"  # Replace with your API key (if required)
    
    # Fetch data from ThingSpeak
    params = {
        "api_key": API_KEY,  # Omit if the channel is public
        "results": 50000  # Adjust as per your data requirement
    }
    response = requests.get(THINGSPEAK_API_URL, params=params)
    
    if response.status_code != 200:
        return render(request, "error.html", {"message": "Failed to fetch data from ThingSpeak."})
    
    data = response.json().get("feeds", [])
    if not data:
        return render(request, "error.html", {"message": "No data available in ThingSpeak."})
    
    # Define local timezone
    local_timezone = pytz.timezone("Asia/Kolkata")  # Adjust timezone as needed
    
    # Get the current date and month
    today = datetime.now(local_timezone).date()
    current_month = today.month
    current_year = today.year
    
    # Create a dictionary with all days from the 1st to today initialized to 0
    daily_usage = {datetime(current_year, current_month, day).date(): 0 for day in range(1, today.day + 1)}
    
    # Process data
    for entry in data:
        utc_time = entry.get("created_at")
        value = entry.get("field2")
        
        if not utc_time or not value:
            continue
        
        # Convert UTC to local time
        utc_time_obj = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%SZ")
        local_time_obj = utc_time_obj.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        
        # Get the local date
        local_date = local_time_obj.date()
        
        # Check if the entry is from the current month and up to today
        if local_date.month == current_month and local_date.year == current_year and local_date <= today:
            # Update the last value for each day
            daily_usage[local_date] = float(value)
    
    # Calculate total water consumed in the month
    total_water = sum(daily_usage.values())
    
    # Convert the result into a sorted list
    sorted_daily_usage = sorted(daily_usage.items())  # Sorted by date
    totalcost = calculate_charges(total_water)
    # Prepare data for template
    context = {
        "dates": [date.strftime("%d-%m-%Y") for date, total in sorted_daily_usage],
        "totals": [total for date, total in sorted_daily_usage],
        "totalwater": total_water,  # Total water consumed in the month
        "totalcost": totalcost,
    }
    
    return render(request, "bill.html", context)