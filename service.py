import uuid
from datetime import datetime
from threading import Thread
from uuid import *

import requests

from db import *
from service import *
from test_status import *

output_file_name = "alltests.txt"

website_collection = get_collection()
tests_collections = get_test_results_collection()


def start_executing_test(request):
    test_handle_id = uuid.uuid4()
    thread = Thread(target=start_test, args=(request, test_handle_id))
    thread.daemon = True
    thread.start()

    test_handle_metadata = {
        "status": "Started",
        "test_handle_id": test_handle_id,
    }
    insert_to_website(test_handle_metadata)
    return {"testHandle": test_handle_id, "status": "Started"}


def start_test(request, test_handle_id):
    iterations = request["iterations"]
    websites = request["websites"]
    res = []
    for website in websites:
        time = []
        start_time = datetime.now()
        for iteration in range(1, iterations + 1):
            time.append(measure_website_time(website))
        data = {
            "test_handle_id": test_handle_id,
            "test_id": uuid.uuid4(),
            "website": website,
            "iterations": iterations,
            "start_time": start_time.timestamp() * 1000,
            "end_time": datetime.now().timestamp() * 1000,
            "max": max(time),
            "min": min(time),
            "avg": sum(time) / iterations
        }
        insert_test_results(data)
        res.append(data)

    outF = open(output_file_name, "a")
    for line in res:
        # write line to output file
        outF.write(str(line))
        outF.write("\n")
    outF.close()

    update_website_status(test_handle_id, TestStatus.COMPLETED.value)


def measure_website_time(website):
    start_time = datetime.now().timestamp() * 1000
    x = requests.get(website)
    print(x.status_code)
    end_time = datetime.now().timestamp() * 1000
    return end_time - start_time


def insert_to_website(data):
    try:
        website_collection.insert_one(data)
        return True
    except Exception as e:
        print("An exception occurred ::", e)
        return False


def update_website_status(test_handle_id, status):
    try:
        update = {"test_handle_id": test_handle_id}
        new_values = {"$set": {"status": status}}
        resp = website_collection.update_one(update, new_values, True)
        return resp.modified_count > 0
    except Exception as e:
        print("An exception occurred ::", e)
        return False


def insert_test_results(test):
    try:
        tests_collections.insert_one(test)
        return True
    except Exception as e:
        print("An exception occurred ::", e)
        return False


def get_test_handle_status(test_handle_id):
    try:
        status = ""
        res = website_collection.find({"test_handle_id": UUID(test_handle_id)}, {"_id": 0})
        for e in res:
            print(e)
            status = e["status"]
            print(status)
        return {"test_handle_id": test_handle_id, "status": status}
    except Exception as e:
        print("An exception occurred", e)
        return {"message": "Unable to retrieve status of " + test_handle_id}


def get_test_results(test_handle_id):
    try:
        status = ""
        res = website_collection.find({"test_handle_id": UUID(test_handle_id)}, {"_id": 0})
        for e in res:
            status = e["status"]
        if status != "Completed":
            return {"message ": "Test in Progress"}

        test_results = []
        results = tests_collections.find({"test_handle_id": UUID(test_handle_id)}, {"_id": 0 , "test_id": 0, "test_handle_id": 0})
        for e in results:
            print(e)
            test_results.append(e)
        return test_results
    except Exception as e:
        print("An exception occurred", e)
        return {"message": "Unable to retrieve test results of " + test_handle_id}
