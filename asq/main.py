from functions import web_search
from pprint import pprint

if __name__ == "__main__":
    data = web_search("MS equity research report")
    pprint(data)
