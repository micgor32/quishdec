from xploreapi.xploreapi import XPLORE
from dotenv import load_dotenv
import os

load_dotenv()

query = XPLORE(os.environ["API_KEY"])
query.abstractText('qr codes')
data = query.callAPI()

print(data)
