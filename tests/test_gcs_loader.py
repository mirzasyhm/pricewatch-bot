import unittest
from unittest.mock import MagicMock, patch
from src.gcs_loader import GCSLoader

class TestGCSLoader(unittest.TestCase):

    @patch('src.gcs_loader.storage.Client')
    def test_upload_file_success(self, mock_client):
        # Setup mocks
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Configure the client to return our mock bucket
        mock_client.return_value.bucket.return_value = mock_bucket
        # Configure the bucket to return our mock blob
        mock_bucket.blob.return_value = mock_blob
        
        # Initialize Loader
        loader = GCSLoader("test-bucket")
        
        # Call the method
        result = loader.upload_file("local_file.json", "remote_path.json")
        
        # Assertions
        self.assertTrue(result)
        mock_bucket.blob.assert_called_with("remote_path.json")
        mock_blob.upload_from_filename.assert_called_with("local_file.json")

    @patch('src.gcs_loader.storage.Client')
    def test_upload_file_failure(self, mock_client):
        # Setup mocks to raise an exception
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
        
        loader = GCSLoader("test-bucket")
        
        result = loader.upload_file("local_file.json", "remote_path.json")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
