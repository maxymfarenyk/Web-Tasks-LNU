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
