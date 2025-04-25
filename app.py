import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
import re
from datetime import datetime, timedelta

app = Flask(__name__)

def scrape_gold_prices():
    url = "https://www.aranypiac.hu/arlista"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all("table")

        gold_data = []
        for table in tables:
            rows = table.find_all("tr")
            if not rows or "Argor-Heraeus" not in table.text:
                continue

            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) < 4:
                    continue
                name = cells[1].get_text(strip=True)
                buy_price = re.sub(r'\D', '', cells[2].text)
                sell_price = re.sub(r'\D', '', cells[3].text)

                if not sell_price or "Argor-Heraeus" not in name:
                    continue

                try:
                    sell_price = int(sell_price)
                    buy_price = int(buy_price) if buy_price else 0
                    final_price = int(sell_price * 1.06)
                except ValueError:
                    continue

                gold_data.append({
                    "name": name,
                    "buy": f"{buy_price:,} Ft",
                    "sell": f"{sell_price:,} Ft",
                    "final": f"{final_price:,} Ft"
                })
        return gold_data
    except Exception as e:
        return str(e)

@app.route("/")
def index():
    data = scrape_gold_prices()
    if isinstance(data, str):
        return f"Hiba történt: {data}"
    return render_template("index.html", gold_data=data)

# 🛠️ Ez kell Renderhez: helyes port binding!
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
