import urllib.request

url = "https://raw.githubusercontent.com/opencv/opencv_contrib/3.4.0/modules/face/data/cascades/haarcascade_mcs_mouth.xml"
filename = "haarcascade_mcs_mouth.xml"

try:
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print("Download completed")
except Exception as e:
    print(f"Download failed: {e}")
