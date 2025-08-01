import requests

url = 'https://ml-notes-kamil.duckdns.org'
try:
    response = requests.get(url, timeout=60)
    print(response.text)
except requests.exceptions.Timeout:
    print("Request timed out.")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
