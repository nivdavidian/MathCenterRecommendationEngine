from locust import HttpUser, task, between

class RecommendationUser(HttpUser):
    wait_time = between(1, 5)  # Simulates a user waiting between 1 to 5 seconds between tasks

    @task
    def get_recommendation(self):
        self.client.post("http://127.0.0.1:8000/api/markov", json={"uid": "16ca9f55", "cCode": "AR", "lCode": "es"})
        

    @task
    def get_recommendation_two(self):
        self.client.post("http://127.0.0.1:8000/api/mostpopular", json={"filters": {'MonthFilter':{'months':[1]}}, "cCode": "AR", "lCode": "es"})