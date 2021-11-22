from pymongo import MongoClient

url = "mongodb+srv://hpe:0x8LEUs3JSUkehAq@cluster0.fnmmr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = MongoClient(url)
db = client["hpe"]
website = db.website
tests = db.tests

def get_collection():
    return website

def get_test_results_collection():
    return tests
