import requests
resp = requests.post("http://127.0.0.1:5000/dependency-check",
                     json={"requirements": "flask>=2.0.0\nrequests>=2.25.1"})
print(resp.json())
