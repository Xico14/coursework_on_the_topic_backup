import os
import json
import requests

from tqdm import tqdm

class VkPhotos:
    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def get_photos(self):
        url = "https://api.vk.com/method/photos.get"
        params = {
            "owner_id": self.user_id,
            "album_id": "profile",
            "extended": 1,
            "count": 5,
            "access_token": self.access_token,
            "v": "5.131"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'response' in data:
            photos = data['response']['items']
        else:
            print("Error retrieving photos")
            photos = []
        return photos

class YandexDisk:
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
                photo_url = max(photo['sizes'], key=lambda x: x['width'] * x['height'])['url']
                status_code = self.upload_photo(photo_url, f"{likes}.jpg", folder_name)
                if status_code == 202:
                    result.append({"file_name": f"{likes}.jpg", "size": "max"})
                pbar.update(1)
        try:
            with open("photos.json", "w") as f:
                json.dump(result, f)
        except Exception as e:
            print(f"Error writing to file: {e}")

if __name__ == '__main__':
    user_id = input("Enter VK user ID: ")
    access_token_yandex = input("Enter Yandex.Disk access token: ")

    access_token_vk = "VK access token"
    VKPhotos_instance = VkPhotos(user_id, access_token_vk)
    YandexDisk_instance = YandexDisk(access_token_yandex)
    photos = VKPhotos_instance.get_photos()
    YandexDisk_instance.save_photos(photos)

