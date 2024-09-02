import base64
import os
from typing import List

from fastapi import status, HTTPException


def save_image_files(output_path: str, image_list: List[str]):
        os.makedirs(output_path, exist_ok=True)

        try:
            for index, image_data in enumerate(image_list):
                image_bytes = base64.b64decode(image_data)
                image_filename = os.path.join(output_path, f"{index}.jpg")
                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)
            return True

        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="파일 경로를 찾을 수 없습니다.")

        except PermissionError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="파일을 생성할 권한이 없습니다.")

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"파일 생성 중 알 수 없는 오류가 발생했습니다: {e}")
