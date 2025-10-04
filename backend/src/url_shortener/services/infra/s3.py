from url_shortener.core.clients.aws import s3_client
import boto3


class PresignedUrl():
      def __init__(self, s3_client) -> None:
            self._s3_client = s3_client

