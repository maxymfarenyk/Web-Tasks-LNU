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

![image](https://github.com/user-attachments/assets/084e0fda-397c-452a-95ec-e2e6a7f5c796)

![image](https://github.com/user-attachments/assets/ba00b701-c9c5-4700-8255-4c1cfec80cdd)

![image](https://github.com/user-attachments/assets/3481b968-8bea-4527-b723-8da103117f69)

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
