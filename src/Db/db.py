from pymongo import MongoClient
def Connect_mongo():
    try:
        url = "mongodb://localhost:27017/"
        db = MongoClient(url)
        collection = db["test"]
        return collection
    except Exception as e:
        print(e)
        return "something wrong happend"