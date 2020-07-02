BASE_URL = "https://quickchart.io/chart?c="
from PIL import Image
from io import BytesIO
from quickchart import QuickChart
import json

def send_data(requests, endpoint):
    resp = requests.get(f"{BASE_URL}{endpoint}")
    if resp.status_code == 200:
        json_data = json.dumps({"url": f"{BASE_URL}{endpoint}"})   
        return f"{BASE_URL}{endpoint}"
    else:
       json_data = json.dumps({"url": False})   
       return json_data

def create_chart(width, height, type, data):
    chart = QuickChart()
    chart.width = width
    chart.height = height
    chart.device_pixel_ration = 2.0
    chart.config = data
    
    return chart.get_url()