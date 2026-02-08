import requests
from requests.auth import HTTPBasicAuth
import pandas
import os

# ~~~ SETUP ~~~
# Lightspeed credentials
key = os.getenv('LIGHTSPEED_KEY')
secret = os.getenv('LIGHTSPEED_SECRET')
baseURL = 'https://api.shoplightspeed.com/us/'
# Men's and Women's IDs
womensIDs = {4547704, 3165569, 3165570, 3165571, 3165572, 3165568, 4149105, 3165573, 3995009, 3165515, 3165517, 3165518, 4149104, 4508225, 3807133, 4440971, 3824583, 4653326, 4572272, 4149106, 3850369, 4624346, 3813367}
mensIDs = {4467161, 4467165, 4467166, 4467167, 4546569, 4546570, 4614909, 4467193, 4546581, 4546582, 3824583, 4631065, 4588392, 4492435, 4572272}

# ~~~ FUNCTIONS ~~~
# Helper function, gets price (including tax), size, and stock amount for each variant of a product
def getAttributes(productID):
    # Get all variants of the product
    url = f'{baseURL}/variants.json?product={productID}' 
    response = requests.get(url, auth=HTTPBasicAuth(key, secret))
    # List to hold variant data
    result = []

    if response.status_code == 200:
        variants = response.json().get('variants', []) # Get all variants
        # For each variant, access ID, price, stock avaliblity, and size. Add that data to the result list
        for variant in variants:
            variantID = variant.get('id')
            price = variant.get('priceIncl', 0)
            stock = variant.get('stockLevel', 0)
            size = variant.get('title', 'Unknown')

            result.append({
                "id": variantID,
                "price": price,
                "stock": stock,
                "size": size
            })
    else:
        print("Fetching variant failed, status code", response.status_code)
        return []
    
    return result

# Helper function, filters for products categorized as men's items   
def filterMens(productID):
    # Get all the categories of a product
    url = f"{baseURL}categories/products.json?product={productID}"
    catResponse = requests.get(url, auth=HTTPBasicAuth(key, secret))

    if catResponse.status_code == 200:
        # Extract data
        categories = catResponse.json()
        category = categories.get('categoriesProducts',[])
        categoryIDs = {item['category']['resource']['id'] for item in category}
        # (debugging) print("Category IDs:", categoryIDs)

        # Determine if the product is a women's product or a men's product
        if categoryIDs & mensIDs:
            return True
        elif categoryIDs & womensIDs:
            return False
        else:
            print("Unrecognized categories:", categoryIDs)
            return False

# Fetch up to 500 products from the API
def getProducts():
    allProducts = 0
    mensProducts = []
    page = 1
    limit = 25
    maxProducts = 150

    while allProducts < maxProducts:
        # Getting products with pagination 
        url = f"{baseURL}products.json?limit={limit}&page={page}"
        # (debugging) print("URL:", url)
        response = requests.get(url, auth=HTTPBasicAuth(key, secret))

        if response.status_code != 200:
            print("Error:", response.status_code, response.text)
            break

        data = response.json() # Converting from JSON for Python
        products = data.get("products",[]) # Safely! get product list

        # Break if no products are returned
        if not products:
            break

        # Determine what type of product each product in the new batch is
        for product in products:
            productID = product.get('id')
            filter = filterMens(productID)

            if  filter == True and product.get('isVisible') and product.get('description') and isinstance(product.get("image"), dict) and product['image'].get('src'):
                # (debugging) print("ProductID:", productID)
                # Add new products to allProducts (avoiding nesting the batch)
                mensProducts.append(product)
        
        page += 1
        allProducts += len(products)

    print("Overall products:", allProducts)
    return mensProducts

# Format each product's data to match Meta Commerce CSV structure
def metaFormat(products):
    rows = []
    
    for product in products:
        # Get attributes of each variant of a product
        variants = getAttributes(product["id"])

        for variant in variants:
            size = variant.get("size", "")
            if size.startswith("Size : "):
                size = size[7:]
            else:
                size = "One size"

            if variant.get("stock", 0) <= 0:
                continue
            
            row = {
                "id": variant["id"],
                "title": product.get("title", ""), # Get to prevent errors
                "description": product.get("description", ""),
                "availability": "in stock" if product.get("isVisible") else "out of stock",
                "condition": "new",
                "price":f"{variant["price"]} USD",
                "link": f"https://www.twinlion.co/{product.get("url", "").lstrip("/")}.html",
                "image_link": product["image"]["src"] if isinstance(product.get("image"), dict) else "", # isinstance to prevent errors
                "brand": "N/A",
                "quantity_to_sell_on_facebook": variant["stock"],
                "size": size,
                "item_group_id": product["id"]
            }
            rows.append(row)

    return pandas.DataFrame(rows)

# ~~~ MAIN ~~~
print("Fetching Twin Lion men's products...")
filteredProducts = getProducts()
print("Total men's products:", len(filteredProducts))

print("Formatting for Meta...")
formattedProducts = metaFormat(filteredProducts)

print("Exporting CSV mensProducts.csv")
formattedProducts.to_csv("mensProducts.csv", index = False)
print("Finished!")



