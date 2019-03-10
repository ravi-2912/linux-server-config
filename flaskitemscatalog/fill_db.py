from sportsitems_db import *

def fillDB():

    crud = CRUD()

    # sample users
    userList = [
        {
            "name": "John Doe",
            "username": "jdoe",
            "password": "jdoe_2007",
            "email": "john.doe@gmail.com"
        },
        {
            "name": "Jane Doe",
            "username": "jane123",
            "password": "jane_2007",
            "email": "janedoe@gmail.com"
        },
        {
            "name": "Simon Michaels",
            "username": "smike",
            "password": "mike_2001",
            "email": "smike@gmail.com"
        }
    ]

    # sample categories
    categoryList = [
        {
            # 1
            "name": "Soccer",
            "user_id": 1
        },
        {
            # 2
            "name": "Basketball",
            "user_id": 2
        },
        {
            # 3
            "name": "Baseball",
            "user_id": 3
        },
        {
            # 4
            "name": "Frisbee",
            "user_id": 1
        },
        {
            # 5
            "name": "Snowboarding",
            "user_id": 2
        },
        {
            # 6
            "name": "Rock Climbing",
            "user_id": 3
        },
        {
            # 7
            "name": "Foosball",
            "user_id": 1
        },
        {
            # 8
            "name": "Skating",
            "user_id": 2
        },
        {
            # 9
            "name": "Hockey",
            "user_id": 3
        }
    ]

    # sample items
    itemList = [
        {
            "name": "Stick",
            "description": "Item Description",
            "quantity": 12,
            "category_id": 9,
            "user_id": 3
        },
        {
            "name": "Goggles",
            "description": "Item Description",
            "quantity": 21,
            "category_id": 5,
            "user_id": 2
        },
        {
            "name": "Snowboard",
            "description": "Item Description",
            "quantity": 5,
            "category_id": 5,
            "user_id": 3
        },
        {
            "name": "Shinquards",
            "description": "Item Description",
            "quantity": 34,
            "category_id": 1,
            "user_id": 1
        },
        {
            "name": "Frisbee",
            "description": "Item Description",
            "quantity": 13,
            "category_id": 4,
            "user_id": 1
        },
        {
            "name": "Bat",
            "description": "Item Description",
            "quantity": 39,
            "category_id": 3,
            "user_id": 3
        },
        {
            "name": "Jersey",
            "description": "Item Description",
            "quantity": 7,
            "category_id": 1,
            "user_id": 1
        },
        {
            "name": "Soccer Cleats",
            "description": "Item Description",
            "quantity": 72,
            "category_id": 1,
            "user_id": 1
        },
        {
            "name": "Ball",
            "description": "Item Description",
            "quantity": 72,
            "category_id": 3,
            "user_id": 1
        }
    ]


    # create users in the table
    for user in userList:
        crud.newUser(user)

    # create categories in the table
    for category in categoryList:
        crud.newCategory(category["name"], category["user_id"])

    # create items in the table
    for item in itemList:
        crud.newItem(item["name"], item["description"],
                    item["quantity"], item["category_id"],
                    item["user_id"])

fillDB()