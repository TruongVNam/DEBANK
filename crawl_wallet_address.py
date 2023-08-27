from core import *

debankUrl = "https://debank.com/whales"
listWhaleAddress = single_object_crawl(debankUrl, 10, None)
transform_and_save_json_file(None, None, "w", listWhaleAddress, None)
