import requests

url = "https://companyenrichment.abstractapi.com/v1/?api_key=7016d04f9ebe46de882fc28f127e2f90&domain=khatabook.com"

response = requests.request("GET", url)

print(response.text)