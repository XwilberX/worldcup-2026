import urllib.request
import os

URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "results.csv")

def download():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, OUTPUT)
    print(f"Saved to {OUTPUT}")
    print(f"Size: {os.path.getsize(OUTPUT):,} bytes")

if __name__ == "__main__":
    download()
