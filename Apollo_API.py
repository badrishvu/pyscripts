url = "https://api.apollo.io/api/v1/organizations/bulk_enrich"

data = {
    "api_key": "YOUR API KEY HERE",
    "domains": [
        "apollo.io",
        "outreach.com",
        "microsoft.com"
    ]
}

headers = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, json=data)

print(response.text)