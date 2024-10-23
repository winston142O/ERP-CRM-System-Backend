import os
import base64
from erp_system_backend.settings import BASE_DIR


class Picture:
    def __init__(self, name: str, folder_path: str, base64_str: str):
        self.name = name
        self.folder_path = folder_path
        self.base64_str = base64_str

    def save_in_path(self, folder_path: str = None):
        """
        Uses the base64 string to save the picture in the provided folder_path.
        """

        # If a folder_path is provided, use it, otherwise, use the default folder_path
        if folder_path:
            self.folder_path = folder_path

        # Decode the base64 string to bytes
        picture_data = base64.b64decode(self.base64_str)

        # Verify that the folder_path exists
        if not os.path.exists(f'{BASE_DIR}/{folder_path}'):
            os.makedirs(f'{BASE_DIR}/{folder_path}')

        # Save the picture in the folder
        with open(f'{BASE_DIR}/{folder_path}/{self.name}', 'wb') as file:
            file.write(picture_data)

    def __str__(self):
        return f"{self.name} ({self.folder_path})"
