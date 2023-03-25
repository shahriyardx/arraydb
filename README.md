# ArrayDb
A database where data is stored in a array of dicts

## Features
- Insert, Update, Delete
- Filter data
- Change/Add columns in database

## Demo
```py
from arraydb import ArrayDb

members = ArrayDb(["username", "age", "gender"], [])

# insert data 
members.insert({"username": "John", "age": 22, "gender": "Male"})
members.insert({"username": "Ayesha", "age": 20, "gender": "Female"})

# Update specific data
members.update(
    where={"username": "John"},
    data={"age": 21}
)

# Even better
members.update(
    where={"age": {"gt": 20}}, # Update all rows where age is greater than 20
    data={"age": 21}
) # gt, lt, gte, lte, not, contains, in, startswith, endswith -> More coming soon
```