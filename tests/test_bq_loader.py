import unittest
from unittest.mock import MagicMock, patch
from src.bq_loader import BigQueryLoader
from google.cloud import bigquery

class TestBigQueryLoader(unittest.TestCase):

    @patch('src.bq_loader.bigquery.Client')
    def test_create_dataset_us(self, mock_client_cls):
        """Test that we request a dataset creation in the US region."""
        # Setup Mock Client
        mock_client = mock_client_cls.return_value
        mock_client.project = "test-project"  # Needs to be a string
        
        # Setup Mock Create Result
        mock_client.create_dataset.return_value = MagicMock()

        loader = BigQueryLoader()
        loader.create_dataset()
        
        # Verify create_dataset was called
        mock_client.create_dataset.assert_called_once()
        
        # Verify the arguments passed to create_dataset
        # args[0] is the dataset object we want to inspect
        call_args = mock_client.create_dataset.call_args
        dataset_arg = call_args[0][0]
        
        self.assertEqual(dataset_arg.location, "US")

    @patch('src.bq_loader.bigquery.Client')
    def test_load_staging_config(self, mock_client_cls):
        """Test that load job config is set to WRITE_TRUNCATE and NDJSON."""
        mock_client = mock_client_cls.return_value
        mock_client.project = "test-project" # Needs to be a string
        
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
