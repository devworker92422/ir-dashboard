import requests

url = "https://drive.google.com/file/d/1b7DALd1Mku7fYrTrwwU6fa-EDsl6v-vE/view?usp=sharing"  # Replace with download URL
r = requests.get(url)

with open("internet-removals-logo-gold-170.png", "wb") as f:
    f.write(r.content)
