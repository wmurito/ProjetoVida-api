import boto3
import os
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class S3UploadService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket = os.getenv('S3_BUCKET')
        self.prefix = 'qrcode-uploads/'
    
    def save_upload(self, session_id: str, file_data: dict):
        """Salva arquivo no S3"""
        key = f"{self.prefix}{session_id}.json"
        data = {
            **file_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        logger.info(f"Arquivo salvo no S3: {key}")
    
    def get_upload(self, session_id: str):
        """Recupera arquivo do S3"""
        key = f"{self.prefix}{session_id}.json"
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = json.loads(response['Body'].read())
            
            # Verificar expiração (5 minutos)
            timestamp = datetime.fromisoformat(data['timestamp'])
            if datetime.utcnow() - timestamp > timedelta(minutes=5):
                self.delete_upload(session_id)
                return None
            
            # Deletar após leitura
            self.delete_upload(session_id)
            return data
        except self.s3_client.exceptions.NoSuchKey:
            return None
    
    def delete_upload(self, session_id: str):
        """Remove arquivo do S3"""
        key = f"{self.prefix}{session_id}.json"
        self.s3_client.delete_object(Bucket=self.bucket, Key=key)

s3_service = S3UploadService()
