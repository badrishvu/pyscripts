import requests
from bs4 import BeautifulSoup

login = "badrish@gumlet.com"
password = "BEN1@badri"
login_url = "https://app.sensortower.com/users/sign_in"
repos_url = "https://app.sensortower.com/overview/com.bhappdevelopment.samwake?country=US"

with requests.session() as s:
    # Step 1: Get login page
    req = s.get(login_url)
    print("Step 1 - Login Page Status Code:", req.status_code)

    # Step 2: Parse the HTML of the login page
    html = BeautifulSoup(req.text, "html.parser")

    # Extract authenticity_token, timestamp, and timestamp_secret
    token = html.find("input", {"name": "authenticity_token"}).attrs["value"]
    time = html.find("input", {"name": "timestamp"}).attrs["value"]
    timeSecret = html.find("input", {"name": "timestamp_secret"}).attrs["value"]

    # Step 3: Prepare payload for login
    payload = {
        "authenticity_token": token,
        "user[email]": login,
        "user[password]": password,
        "timestamp": time,
        "timestamp_secret": timeSecret
    }

    # Step 4: Perform login
    res = s.post(login_url, data=payload)
    print("Step 4 - Login Status Code:", res.status_code)

    # Step 5: Access the repos_url after logging in
    r = s.get(repos_url)
    print("Step 5 - Repositories Page Status Code:", r.status_code)

    # Step 6: Parse the HTML of the repositories page
    soup = BeautifulSoup(r.content, "html.parser")

    # Step 7: Extract information from the page
    usernameDiv = soup.find("div", class_="AppOverviewKpiBase-module__valueContainer--eAXSE")
    print("Username: " + usernameDiv.getText())

    repos = soup.find_all("div", class_="AppOverviewKpiBase-module__valueContainer--eAXSE")
    for r in repos:
        repoName = r.find("div").getText()
        print("Repository Name: " + repoName)
