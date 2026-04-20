import os, requests, time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
COOKIE_STRING = "Your cookie string value"
APP_ID = "1551360"
DOWNLOAD_BASE = "FH5_Cloud_Recovery"
# ---------------------

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Cookie": COOKIE_STRING
}

def download_saves():
    if not os.path.exists(DOWNLOAD_BASE):
        os.makedirs(DOWNLOAD_BASE)

    session = requests.Session()
    session.headers.update(headers)
    
    index = 0
    total_downloaded = 0
    
    print(f"[*] Starting deep recovery for AppID {APP_ID}...")

    while True:
        url = f"https://store.steampowered.com/account/remotestorageapp/?appid={APP_ID}&index={index}"
        print(f"[*] Fetching page (index {index})...")
        
        try:
            response = session.get(url)
            if response.status_code != 200:
                print(f"[!] Access Denied or Session Expired at index {index}.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for the table rows
            rows = soup.find_all('tr')[1:] # Skip header
            
            if not rows:
                print("[*] No more files found. Finishing...")
                break

            page_downloads = 0
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                # Column 1 is usually the Filename
                relative_path = cols[1].text.strip()
                
                # Logic: Look for a link in ANY column to avoid index mismatch
                link_element = row.find('a', href=True)
                
                if not link_element or 'download' not in link_element['href'].lower():
                    continue
                
                download_url = link_element['href']
                local_path = os.path.join(DOWNLOAD_BASE, relative_path)
                
                # Ensure subfolders exist
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                try:
                    file_data = session.get(download_url)
                    with open(local_path, 'wb') as f:
                        f.write(file_data.content)
                    page_downloads += 1
                    total_downloaded += 1
                    if total_downloaded % 10 == 0:
                        print(f"[+] Progress: {total_downloaded} files saved...")
                except Exception as e:
                    print(f"[!!] Failed {relative_path}: {e}")
            
            if page_downloads == 0:
                # If we scanned a page and found 0 valid download links, we've hit the end
                break
                
            # Move to the next page of 50 files
            index += 50
            time.sleep(0.5) # Be kind to Steam's servers to avoid IP bans

        except Exception as e:
            print(f"[!] Critical Error: {e}")
            break

    print(f"\n[+] SUCCESS: {total_downloaded} files recovered to '{DOWNLOAD_BASE}'.")

if __name__ == "__main__":
    download_saves()