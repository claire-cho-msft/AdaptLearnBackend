import requests
from bs4 import BeautifulSoup
from selenium import webdriver

url = "https://learn.microsoft.com/en-us/azure/ai-services/openai/supported-languages?tabs=dotnet-secure%2Csecure%2Cpython-secure%2Ccommand&pivots=programming-language-python"

driver = webdriver.Chrome()
driver.get(url)

soup = BeautifulSoup(driver.page_source, "html.parser")
content = soup.get_text()

main = (
        soup.find("main")
        or soup.find(id="main")
        # or soup.find("article")
        or soup.find("content")
        or soup.body
    )

with open ("web.html", "w") as f:
    f.write(main.prettify())



