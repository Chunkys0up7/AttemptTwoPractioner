"""
Test data for MCP and workflow API tests.
"""

MCP_TEST_DATA = {
    "name": "Test MCP Definition",
    "description": "This is a test MCP definition",
    "external_db_config": {
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "user": "test_user",
        "password": "test_password",
        "schema": "public"
    },
    "mcp_type": "test_type",
    "config_payload_data": {
        "key": "value",
        "settings": {
            "timeout": 30,
            "retry_count": 3
        }
    }
}

WORKFLOW_TEST_DATA = {
    "name": "Test Workflow",
    "description": "This is a test workflow",
    "mcp_id": "",  # Will be populated during tests
    "steps": [
        {
            "name": "Step 1",
            "type": "data_extraction",
            "config": {
                "source": "database",
                "query": "SELECT * FROM test_table"
            }
        },
        {
            "name": "Step 2",
            "type": "data_transformation",
            "config": {
                "operations": [
                    {"type": "filter", "field": "status", "value": "active"},
                    {"type": "sort", "field": "created_at", "order": "desc"}
                ]
            }
        }
    ]
}

DASHBOARD_TEST_DATA = {
    "name": "Test Dashboard",
    "description": "This is a test dashboard",
    "layout": {
        "widgets": [
            {
                "type": "table",
                "title": "Data Overview",
                "data_source": "workflow_1",
                "columns": ["id", "name", "status"]
            },
            {
                "type": "chart",
                "title": "Status Distribution",
                "chart_type": "pie",
                "data_source": "workflow_2",
                "series": ["status"]
            }
        ]
    }
}

test_data = {
    "mcp": MCP_TEST_DATA,
    "workflow": WORKFLOW_TEST_DATA,
    "dashboard": DASHBOARD_TEST_DATA
}
