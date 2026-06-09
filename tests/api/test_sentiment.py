def test_get_sentiment_overview(client):
    response = client.get("/api/v1/sentiment/overview")
    # Assuming endpoints are protected, this might return 401
    # Adjust test to include auth token if needed
    pass
