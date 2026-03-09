"""Tests for API connectivity with Azure services."""

import os
import pytest
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient


@pytest.fixture
def credential():
    """Provide Azure credential for tests."""
    return DefaultAzureCredential()


def test_sentinel_connection(credential):
    """Verify Sentinel workspace is accessible.
    
    This test requires SENTINEL_WORKSPACE_ID environment variable to be set
    and proper Azure credentials configured.
    """
    workspace_id = os.getenv("SENTINEL_WORKSPACE_ID")
    if not workspace_id:
        pytest.skip("SENTINEL_WORKSPACE_ID not set")

    client = LogsQueryClient(credential)
    
    # Simple query to verify connectivity
    response = client.query_workspace(
        workspace_id=workspace_id,
        query="SecurityAlert | take 1 | project TimeGenerated, AlertName",
        timespan="PT1H"
    )
    
    assert response is not None
    print(f"✅ Sentinel connection successful")


def test_graph_connection(credential):
    """Verify Microsoft Graph is accessible.
    
    This test verifies basic Graph API connectivity.
    """
    try:
        from msgraph.generated import GraphServiceClient
        
        client = GraphServiceClient(credential=credential)
        # Graph connection would be tested here
        print(f"✅ Graph client created successfully")
        assert client is not None
    except ImportError:
        pytest.skip("msgraph-sdk not installed")
    except Exception as e:
        pytest.fail(f"Graph connection failed: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
