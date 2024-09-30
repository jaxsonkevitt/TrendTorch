import json
import requests
import os
from dotenv import load_dotenv

def filter_trends():
    # Read the trending_searches.json file
    with open('trending_searches.json', 'r') as f:
        trends = json.load(f)

    # Filter trends with spike percentage >= 5%
    filtered_trends = [trend for trend in trends if trend['spike_percentage'] >= 10]

    # Write the filtered trends to a new JSON file
    with open('filtered_trends.json', 'w') as f:
        json.dump(filtered_trends, f, indent=2)

    print(f"Original trends: {len(trends)}")
    print(f"Filtered trends: {len(filtered_trends)}")
    print("Filtered trends saved to 'filtered_trends.json'")

if __name__ == "__main__":
    filter_trends()

