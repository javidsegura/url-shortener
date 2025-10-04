from enum import Enum
from mypy_boto3_s3.client import S3Client
from url_shortener.core.clients.aws import s3_client

class PresignedUrlActionsType(Enum):
      PUT =  "put_object"
      GET = "get_object" 

class PresignedUrl():
      
      def _generate_url(self, action_type: PresignedUrlActionsType,
                                        s3_bucket_name: str,
                                        key: str,
                                        expiration_time_secs:int = 3600,
                                        **kwargs):
            presigned_url = s3_client.generate_presigned_url(
                  ClientMethod=action_type.value,
                  Params={
                        "Bucket": s3_bucket_name,
                        "Key": key,
                        **{str(key): value for key, value in kwargs.items()}
                  },
                  ExpiresIn=expiration_time_secs
            )
            return presigned_url
      def get_presigned_url(self, s3_bucket_name: str, key: str, expiration_time_secs:int = 3600, **kwargs) -> str:
            return self._generate_url(
                  action_type=PresignedUrlActionsType.GET,
                  s3_bucket_name=s3_bucket_name,
                  key=key,
                  expiration_time_secs=expiration_time_secs,
                  **kwargs
            )
      def put_presigned_url(self, s3_bucket_name: str, key: str, expiration_time_secs:int = 3600, **kwargs) -> str:
            return self._generate_url(
                  action_type=PresignedUrlActionsType.PUT,
                  s3_bucket_name=s3_bucket_name,
                  key=key,
                  expiration_time_secs=expiration_time_secs,
                  **kwargs
            )

