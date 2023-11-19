import requests
import json
from tqdm import tqdm

class vk_photos:
    def __init__(self, user_id, access_token, url):
        self.user_id = user_id
        self.access_token = access_token
        self.url = url

    def get_photos(self):
        headers = {"Authorization": f"OAuth {self.access_token}"}
        response = requests.get(self.url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'response' in data:
            photos = data['response']['items']
        else:
            print("Error retrieving photos")
            photos = []
        return photos

class yandex_disk:
    def __init__(self, access_token):
        self.access_token = access_token

    def create_folder(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {"Authorization": f"OAuth {self.access_token}"}
        params = {"path": folder_name}
        response = requests.put(url, headers=headers, params=params)
        if response.status_code == 409:
            print(f"Folder '{folder_name}' already exists.")
            return
        response.raise_for_status()
        return response.status_code

    def upload_photo(self, photo_url, file_name, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {"Authorization": f"OAuth {self.access_token}"}
        params = {"path": f"{folder_name}/{file_name}", "url": photo_url}
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        return response.status_code

    def save_photos(self, photos):
        folder_name = "img"
        self.create_folder(folder_name)
        result = []
        with tqdm(total=len(photos), desc="Uploading photos") as pbar:
            for photo in photos:
                likes = photo['likes']['count']
                date = photo['date']
                photo_url = photo['sizes'][-1]['url']
                status_code = self.upload_photo(photo_url, f"{likes}.jpg", folder_name)
                if status_code == 202:
                    result.append({"file_name": f"{likes}.jpg", "size": "z"})
                pbar.update(1)
        try:
            with open("photos.json", "w") as f:
                json.dump(result, f)
        except Exception as e:
            print(f"Error writing to file: {e}")

user_id = input("Enter VK user ID: ")
access_token_vk = 'vk1.a.l-RjfRQvzqPj82h8dh0BnUqnqHLpTrnjFDZ-0ZmPb5e1jtmBs8xYmNgE276GvCo0fFTiwCIGpF-vM4Z0rwYKsL70UscF8OC7hHIHvEee1BECeVpOJKcym-ap_Q9jwS9m4n_esPFF7f-2eTVLynz8zgUS2q1hxP0tshaGLtJ_3gNQcGmq-ouDYwJjrHHB0bTsFoesm6tOJQ9pbkdC3a3n4w'
access_token_yandex = input("Enter Yandex.Disk token: ")

vk_photos_instance = vk_photos(user_id, access_token_vk, f"https://api.vk.com/method/photos.get?owner_id={user_id}&album_id=profile&extended=1&count=5&access_token={access_token_vk}&v=5.131")
yandex_disk_instance = yandex_disk(access_token_yandex)

photos = vk_photos_instance.get_photos()
yandex_disk_instance.save_photos(photos)

