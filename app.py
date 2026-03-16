from flask import Flask
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

KEYWORD = "iphone 11"


def mercari_price(keyword):

    url = f"https://jp.mercari.com/search?keyword={keyword}&status=sold_out"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.text,"html.parser")

    prices = []

    for p in soup.select("span[data-testid='price']")[:20]:

        try:
            price = int(p.text.replace("¥","").replace(",",""))
            prices.append(price)
        except:
            pass

    if len(prices)==0:
        return 0

    return int(sum(prices)/len(prices))


def yahoo_items(keyword):

    url = f"https://auctions.yahoo.co.jp/search/search?p={keyword}&fixed_price=1"

    headers = {
        "User-Agent":"Mozilla/5.0"
    }

    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.text,"html.parser")

    items = soup.select("li.Product")

    data=[]

    for item in items[:10]:

        try:

            title=item.select_one("h3").text.strip()

            price=item.select_one(".Product__priceValue").text
            price=int(price.replace("円","").replace(",",""))

            link=item.select_one("a")["href"]

            data.append({
                "title":title,
                "price":price,
                "url":link
            })

        except:
            pass

    return data


@app.route("/")
def home():

    mercari=mercari_price(KEYWORD)

    items=yahoo_items(KEYWORD)

    html="<h1>スマホ転売AI</h1>"

    html+=f"<h2>メルカリ相場 {mercari}円</h2>"

    html+="<h2>利益ランキング</h2>"

    for i in items:

        profit=mercari-i["price"]

        html+=f"""
        <p>
        {i['title']} <br>
        仕入 {i['price']}円 <br>
        利益 {profit}円 <br>
        <a href='{i['url']}'>ヤフオクを見る</a>
        </p>
        """

    html+="<p>5分ごと更新</p>"

    return html


if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
