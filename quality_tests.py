from locust import task, HttpUser, between

USERNAME = 'limi'
PASSWORD = 'limi'


class GuestUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def home_page(self):
        self.client.get(url='')

    @task
    def registration_page(self):
        self.client.get(url='/registration')

    @task
    def registration_success_page(self):
        self.client.get(url='/registration/success')

    @task
    def rank_page(self):
        self.client.get(url='/rank/')


class JudgeUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.get("/login/")
        csrftoken = response.cookies['csrftoken']
        self.client.post('/login/',
                         {'username': USERNAME, 'password': PASSWORD},
                         headers={'X-CSRFToken': csrftoken})

    @task
    def rank_page(self):
        self.client.get(url='/rank/')

    @task
    def tasks_page(self):
        self.client.get(url='/tasks/')

    @task
    def task_create_page(self):
        self.client.get(url='/tasks/create/')

    @task
    def task_edit_page(self):
        self.client.get(url='/tasks/1')

    @task
    def solutions_page(self):
        self.client.get(url='/solutions/')

