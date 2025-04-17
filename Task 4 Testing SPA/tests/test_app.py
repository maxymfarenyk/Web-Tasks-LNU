import pytest
from app import app, init_db

@pytest.fixture
def client(tmp_path):

    test_db = tmp_path / "test_users.db"
    app.config['TESTING'] = True
    app.config['DB_PATH'] = str(test_db)

    with app.test_client() as client:
        init_db()
        yield client


def test_register_login_logout(client):
    # Реєстрація
    client.post('/register', data={
        'username': 'testuser',
        'firstname': 'Test',
        'lastname': 'User',
        'password': 'password123'
    })

    # Логін
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # редірект

    # Вихід
    response = client.get('/logout')
    assert response.status_code == 302
