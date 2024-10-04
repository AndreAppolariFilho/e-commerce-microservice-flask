#E-COMMERCE flask microservices

## Description

Simple microservices to pratice some skill.

## Running the project

It's necessary to have docker installed in your computer, in the root of the project run the
following command.

    docker-compose up --build

## Ideas for future development

* Update the stock's quantity when one item is added to the cart;
* If the same product is added twice, group then in one line;
* Enables the possibility of cancelling the shopping cart, updating the stock;
* Validation for making sure that it won't be possible to add items in the shopping cart that doesn't have stock;

## API'S Calls

POST | /register | Creates a new user

Only admin users can create products.

Body
    
{
        "username":"new_user", 
        "password":"test",
        "is_admin": "true"
    }

Responses

200 {
        "username":"new_user", 
        "password":"test",
        "is_admin": "true"
    }

Curl example

    curl -d '{"username":"new_user", "password":"test", "is_admin": "true"}' -H "Content-Type: application/json" -X POST http://localhost:5001/register
    
POST | /login | Retrieves a new JWT token for the account
Body
 {
        "username":"new_user", 
        "password":"test"
    }
Responses

200 {
       "access_token": JWT_TOKEN
    }

    `curl -d '{"username":"new_user", "password":"test"}' -H "Content-Type: application/json" -X POST http://localhost:5001/login`


POST | /validate | Validate the token and return the user relevant information

Responses

200 {
        "username":"new_user", 
        "password":"test",
        "is_admin": "true"
    }

    `curl -d '{"username":"new_user", "password":"test"}' -H "Content-Type: application/json" -X POST http://localhost:5001/validate`


POST | /products | Validate the token and return the user relevant information

Body
{
    "name":"Nintendo Switch", 
    "category":"video games"
}

Responses

200 {
    "name":"Nintendo Switch", 
    "category":"video games"
}

    curl -d '{"name":"Nintendo Switch", "category":"video games"}' -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -X POST http://localhost:5002/products

POST | / products/id/stocks | Creates stock information for the product

Body
{
    "price":"640", 
    "quantity":"100"
}

Responses

{
    "price":"640", 
    "quantity":"100"
}

GET | / products/id/stocks | Retrieves information about the product and the stock

Responses

{
    "id": 1,
    "price": "1000.00",
    "quantity": "100",
    "name": "Product",
    "category": "Category"
}

    curl -d '{"price":"640", "quantity":"100"}' -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -X POST http://localhost:5002/products/1/stocks

POST | /shopping_carts | Creates a shopping cart or add the item for the already existing cart, it ensures that each user only have one shopping cart

Body

{
    "product_id":"1", 
    "quantity":"1"
}

Responses

200
{
    "id": 1,
    "username": "user",
    "items": [
        {
            "id": 1,
            "price": "1000.00",
            "quantity": "100",
            "product_id": "1",
            "product_name": "Nintendo Switch",
            "product_category": "video games"
        },
    ]
}

    curl -d '{"product_id":"1", "quantity":"1"}' -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -X POST http://localhost:5003/shopping_carts

GET | /shopping_carts | Retrieves the user's shopping cart and it's items

Responses

200
{
    "id": 1,
    "username": "user",
    "items": [
        {
            "id": 1,
            "price": "1000.00",
            "quantity": "100",
            "product_id": "1",
            "product_name": "Nintendo Switch",
            "product_category": "video games"
        },
    ]
}

    curl -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN" -X POST http://localhost:5003/shopping_carts