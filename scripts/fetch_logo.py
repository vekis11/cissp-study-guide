import re
import urllib.request

url = "https://www.linkedin.com/company/temtech-solutions"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
imgs = list(dict.fromkeys(re.findall(r"https://media\.licdn\.com/dms/image/[^\"&<>]+", html)))
for u in imgs:
    if "tem_tech" in u.lower() or "temtech" in u.lower():
        print("LOGO:", u)
