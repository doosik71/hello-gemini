import io
import os
import base64


class FileStore:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _encode_name(self, name: str) -> str:
        """
        name 문자열을 base64로 인코딩하여 안전한 파일 이름으로 변환.
        """

        encoded = base64.urlsafe_b64encode(name.encode("utf-8")).decode("ascii")
        return encoded

    def __setitem__(self, name: str, data: str) -> None:
        """
        name을 base64로 인코딩하여 파일 이름으로 사용.
        해당 경로에 텍스트 파일로 data 저장.
        """

        encoded_name = self._encode_name(name)
        file_path = os.path.join(self.data_dir, encoded_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)

    def __getitem__(self, name: str) -> str:
        """
        name을 base64로 인코딩하여 파일 이름 확보.
        해당 파일이 존재하면 내용을 반환, 없으면 None 반환.
        """

        encoded_name = self._encode_name(name)
        file_path = os.path.join(self.data_dir, encoded_name)

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
