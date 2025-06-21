import json
import time
import random
from google.cloud import pubsub_v1

# Set your project and topic
project_id = "your-gcp-project-id"
topic_id = "your-topic-id"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def generate_data():
    return {
        "user_id": random.randint(1, 100),
        "action": random.choice(["click", "view", "purchase"]),
        "timestamp": time.time()
    }

while True:
    data = json.dumps(generate_data()).encode("utf-8")
    publisher.publish(topic_path, data=data)
    print("Published:", data)
    time.sleep(3)  # publish every 3 seconds
