import asyncio
from aiobotocore.session import get_session
from contextlib import asynccontextmanager

from pathlib import Path

from typing import BinaryIO
from src.core.s3.config import s3_settings


class S3Client:
    
    def __init__(
            self,
            bucket_name: str
        ):
        
        self.config = s3_settings.model_dump()

        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client
    
    async def upload_file(self, filename: str, file: BinaryIO):
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file.read()
            )
    
    async def delete_file(self, key: str):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
    
    async def get_presigned_url(self, key: str):
        async with self.get_client() as client:
            presigned_url = await client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    'Bucket':self.bucket_name,
                    'Key': key,
                },
                ExpiresIn=3600
            )
            print(presigned_url)
            return presigned_url


if __name__ == '__main__':
    s3 = S3Client("flows-app-avatars-bucket")
    asyncio.run(s3.get_presigned_url("warlord.jpg"))