import urllib.request
from pathlib import Path

LOGO_URL = (
    "https://media.licdn.com/dms/image/v2/D560BAQFm66LXVpHk-w/"
    "company-logo_200_200/B56ZxTKoaCKIAI-/0/1770921822136/"
    "tem_tech_solutions_llc_logo?e=2147483647&v=beta"
)
out = Path(__file__).resolve().parents[1] / "frontend" / "public" / "branding"
out.mkdir(parents=True, exist_ok=True)
dest = out / "temtech-logo.png"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.linkedin.com/company/temtech-solutions/",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}
req = urllib.request.Request(LOGO_URL, headers=headers)
data = urllib.request.urlopen(req, timeout=30).read()
dest.write_bytes(data)
print(f"Saved {len(data)} bytes to {dest}")
