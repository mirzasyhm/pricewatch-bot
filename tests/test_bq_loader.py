import unittest
from unittest.mock import MagicMock, patch
from src.bq_loader import BigQueryLoader
from google.cloud import bigquery

class TestBigQueryLoader(unittest.TestCase):

    @patch('src.bq_loader.bigquery.Client')
    def test_create_dataset_us(self, mock_client_cls):
        """Test that we request a dataset creation in the US region."""
        mock_client = mock_client_cls.return_value
        mock_dataset_ref = MagicMock()
        mock_client.dataset.return_value = mock_dataset_ref
        
        loader = BigQueryLoader()
        loader.create_dataset()
        
        # Verify we set location to US
        self.assertEqual(mock_dataset_ref.location, "US")
        # Verify create_dataset was called
        mock_client.create_dataset.assert_called_once()

    @patch('src.bq_loader.bigquery.Client')
    def test_load_staging_config(self, mock_client_cls):
        """Test that load job config is set to WRITE_TRUNCATE and NDJSON."""
        mock_client = mock_client_cls.return_value
        
        loader = BigQueryLoader()
        loader.load_staging_table("gs://test/file.json")
        
        # Get the job config passed to load_table_from_uri
        # args[0] is uri, args[1] is table_ref
        # kwargs['job_config'] is what we want
        call_args = mock_client.load_table_from_uri.call_args
        job_config = call_args.kwargs['job_config']
        
        self.assertEqual(job_config.write_disposition, bigquery.WriteDisposition.WRITE_TRUNCATE)
        self.assertEqual(job_config.source_format, bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)

if __name__ == '__main__':
    unittest.main()
