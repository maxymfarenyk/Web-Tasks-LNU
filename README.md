# Web-Tasks-LNU

## Task 4. Testing

Використовуємо веб-застосунок із [Task 3](https://github.com/maxymfarenyk/Web-Tasks-LNU/tree/main/Task%203%20SPA_App)

### 1. Testing Coverage 30%

Створюємо tests/**test_app.py**

```
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

```

![image_2025-04-17_13-21-21](https://github.com/user-attachments/assets/ccfdf647-802f-4313-8f4d-f638b1c8dc98)


### 2. Performance test

Створюємо tests/**locustfile.py**

```
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def complex_scenario(self):
        self.client.post("/register", data={
            "username": "perfuser",
            "firstname": "Perf",
            "lastname": "User",
            "password": "12345"
        })

        response = self.client.post("/login", data={
            "username": "perfuser",
            "password": "12345"
        }, allow_redirects=False)

        token = response.cookies.get("token")
        cookies = {"token": token}

        self.client.get("/info", cookies=cookies)
```
![image](https://github.com/user-attachments/assets/ca4caa94-ef01-47b3-bb19-52bf53c6df69)

![image](https://github.com/user-attachments/assets/9051beec-87e5-405d-9bbb-4129f4c3023c)

![image](https://github.com/user-attachments/assets/168e3a53-fca8-41da-956b-4665690288f9)

![image](https://github.com/user-attachments/assets/6ef7988f-96c2-492b-8020-4d0f2b4ec6de)

### 3. Scraping

Створюємо tests/**scraper.py**

```
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("http://localhost:5000/login")
time.sleep(1)

driver.find_element(By.NAME, "username").send_keys("Serhiy2512")
driver.find_element(By.NAME, "password").send_keys("5555")
driver.find_element(By.XPATH, "//button[@type='submit']").click()

time.sleep(1)
driver.get("http://localhost:5000/profile")


lastname = driver.find_element(By.ID, "lastname").text
firstname = driver.find_element(By.ID, "firstname").text
print(f"Full name is {firstname} {lastname}")

driver.quit()
```

![image](https://github.com/user-attachments/assets/a7344238-35b8-43ce-9c38-32b60f73f0b8)
