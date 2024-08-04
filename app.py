from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time
import re

app = Flask(__name__)

# Setup WebDriver
service = Service('C:/Users/(Users)/Downloads/msedgedriver.exe')  # Set msedgedriver.exe path, Users need to write the computer user name
driver = webdriver.Edge(service=service)

product_name = 'Yeo\'s Soya Bean'
target_price = 4

products = []

def find_closest_product(products, target_price):
    product_prices = {}
    closest_product = None
    closest_price_diff = float('inf')  # Initialize with a large number

    for i, product in enumerate(products):
        if i >= 10:  # Stop after 10 iterations
            break
        try:
            title = product['title']
            price_text = product['price']
            price = float(re.sub(r'[^\d.]', '', price_text))  # Convert price to float

            # Collect prices for the same product name
            if title not in product_prices:
                product_prices[title] = []
            product_prices[title].append(price)

            # Calculate price difference
            price_diff = abs(price - target_price)
            
            if price_diff < closest_price_diff:
                closest_price_diff = price_diff
                closest_product = {
                    'name': title,
                    'price': price,
                    'link': product['lazada_link']  # Assuming you want to use Lazada link
                }

        except Exception as e:
            print(f"Error processing product: {e}")

    # Update the closest product to the cheapest price for the same name
    if closest_product:
        closest_name = closest_product['name']
        cheapest_price = min(product_prices[closest_name])
        closest_product['price'] = cheapest_price
        closest_product['link'] = next(
            (p['lazada_link'] for p in products 
             if p['title'].strip() == closest_name and 
             float(re.sub(r'[^\d.]', '', p['price'].strip())) == cheapest_price), 
            'Link not found'
        )
        
    return closest_product

try:
    # Open the website
    driver.get("https://www.hargapedia.com.my/")

    # Wait
    driver.implicitly_wait(10)  # 最大等待时间10秒钟

    # Find “fominimize” element
    time.sleep(5)  # 等待广告加载完成
    try:
        fominimize = driver.find_element(By.CSS_SELECTOR, ".fominimize img")
        fominimize.click()
    except:
        pass

    # Search for the search bar
    search_box = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search & Compare to Save!']")
    search_box.send_keys(product_name)
    
    search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    search_button.click()

    time.sleep(10)

    # Find the container that include the search data
    product_containers = driver.find_elements(By.CSS_SELECTOR, ".styles_productcardContainer__e6fx1")

    # Print debug information for each container
    for index, container in enumerate(product_containers):
        print(f"Processing container {index + 1}")

        try:
            title_element = container.find_element(By.CSS_SELECTOR, "h4 > div")
            title = title_element.text
            print(f"Title: {title}")

            price_element = container.find_element(By.CSS_SELECTOR, ".styles_price__162Vn")
            price = price_element.text
            print(f"Price: {price}")

            lazada_link = container.find_element(By.CSS_SELECTOR, "a[href*='lazada']").get_attribute("href")
            shopee_link = container.find_element(By.CSS_SELECTOR, "a[href*='shopee']").get_attribute("href")
            print(f"Lazada Link: {lazada_link}")
            print(f"Shopee Link: {shopee_link}")

            product_info = {
                'title': title,
                'price': price,
                'lazada_link': lazada_link,
                'shopee_link': shopee_link
            }

            products.append(product_info)

        except Exception as e:
            print(f"Error extracting product info: {e}")

    # Find the closest product after collecting all products
    closest_product = find_closest_product(products, target_price)
    print(f"Closest Product: {closest_product}")

finally:
    driver.quit()

# Setup the Flask
@app.route('/search_results', methods=['GET'])
def search_results():
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=False)
