from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)
    host = "http://localhost"

    @task(3)
    def view_homepage(self):
        self.client.get("/", name="/")

    @task(2)
    def view_about_page(self):
        self.client.get("/about.html", name="/about.html")

    @task(1)
    def view_blog_page(self):
        self.client.get("/blog.html", name="/blog.html")

    @task(5)
    def use_chatbot(self):
        messages = [
            "مرحبا، كيف يمكنني المساعدة؟",
            "أرغب في معرفة المزيد عن حلولكم التسويقية.",
            "ما هي أحدث خدماتكم؟",
            "هل تقدمون استشارات مجانية؟",
            "أحتاج إلى مساعدة في تصميم شعار."
        ]
        self.client.post("/chatbot/chat", json={"message": random.choice(messages)}, name="/chatbot/chat")

    @task(1)
    def send_websocket_message(self):
        # This task assumes a simple WebSocket endpoint for testing.
        # In a real scenario, you would use a WebSocket client library.
        # For HTTP-based load testing, we can simulate a POST to a WebSocket API gateway if available.
        # For now, we'll simulate a generic POST request that might trigger a WebSocket event.
        self.client.post("/ws/send_message", json={"user": "test_user", "message": "Hello via WebSocket!"}, name="/ws/send_message")

    @task(1)
    def view_admin_dashboard(self):
        # Simulate accessing the admin dashboard (requires authentication)
        # For simplicity, we're just hitting the URL. In a real test, you'd handle login.
        self.client.get("/admin/", name="/admin/")

    @task(1)
    def view_client_portal(self):
        # Simulate accessing the client portal
        self.client.get("/client_portal/", name="/client_portal/")

    @task(1)
    def view_team_management(self):
        # Simulate accessing the team management system
        self.client.get("/team_management/", name="/team_management/")

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    host = "http://localhost"

    @task(5)
    def access_admin_panel(self):
        self.client.get("/admin/", name="/admin/")

    @task(2)
    def create_new_post(self):
        # Simulate creating a new post in the admin panel
        self.client.post("/admin/cms/post/add/", name="/admin/cms/post/add/")

class ClientUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost"

    @task(5)
    def access_client_dashboard(self):
        self.client.get("/client_portal/dashboard.html", name="/client_portal/dashboard.html")

    @task(2)
    def view_project_progress(self):
        self.client.get("/client_portal/project_progress", name="/client_portal/project_progress")

class TeamUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost"

    @task(5)
    def access_team_dashboard(self):
        self.client.get("/team_management/dashboard.html", name="/team_management/dashboard.html")

    @task(2)
    def update_task_status(self):
        self.client.post("/team_management/update_task", json={"task_id": 1, "status": "completed"}, name="/team_management/update_task")

