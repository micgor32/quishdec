import requests
from dotenv import load_dotenv
import os


load_dotenv()  # take environment variables from .env.


API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.springernature.com/meta/v2/json'

params = {
    'q': 'keyword:"Qr code"', 
    'api_key': API_KEY
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()  
    for record in data['records']:
    
        title = record.get('title', 'No title available')
        print(f"Title: {title}")

        authors = record.get('creators', [])
        if authors:
            author_names = ', '.join([author['creator'] for author in authors])
            print(f"Authors: {author_names}")
        else:
            print("Authors: No authors available")
else:
    print(f"Failed to retrieve data: {response.status_code}")
