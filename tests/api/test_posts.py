def test_create_post(client):
    # Register and login to get token
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "post@example.com",
            "password": "securepassword123",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "post@example.com", "password": "securepassword123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/posts/",
        json={
            "platform": "twitter",
            "author_name": "tech_guru",
            "content": "This new platform is absolutely amazing!",
            "source_id": "123456",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "twitter"
    assert "id" in data


def test_list_posts(client):
    # Assuming the previous test created a post, or create one here
    response = client.get("/api/v1/posts/")
    # If unauthenticated, it might return 401 depending on your routes.
    # Adjust according to your security dependencies.
