import requests

response = requests.post("http://localhost:5000/query", json={"question": "What it microcentre's return policy?"})
print(response.json())
