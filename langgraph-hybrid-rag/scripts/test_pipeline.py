import requests
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def test_rag_pipeline():
    # 1. Upload document
    print("Uploading test document...")
    path = os.path.join(os.path.dirname(__file__), "../test_documents/aws_well_architected_framework.pdf")
    path = os.path.abspath(path)
    with open(path, "rb") as f:
        response = requests.post(f"{BASE_URL}/ingest", files={"file": f})
    response.raise_for_status()
    chunks = response.json()["data"]["chunks_created"]
    assert chunks >= 100, f"Unexpected chunks: {chunks}"

    # 2. Test keyword query
    print("Testing keyword search...")
    response = requests.post(f"{BASE_URL}/query", json={"question": "What is the purpose of a staging environment?"})
    result = response.json()
    assert result["success"]
    assert len(result["data"]["citations"]) > 0

    # 3. Test semantic query
    print("Testing semantic search...")
    response = requests.post(f"{BASE_URL}/query", json={"question": "How do we test changes before going live?"})
    result = response.json()
    assert result["success"]
    assert len(result["data"]["citations"]) > 0

    # 4. Test no results
    print("Testing no results case...")
    response = requests.post(f"{BASE_URL}/query", json={"question": "Recipe for pizza?"})
    result = response.json()
    assert result["success"]
    assert "cannot find" in result["data"]["answer"].lower()

    print("✅ All tests passed!")


if __name__ == "__main__":
    test_rag_pipeline()
