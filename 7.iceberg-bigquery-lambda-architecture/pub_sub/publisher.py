#!/usr/bin/env python3
"""
Simple Pub/Sub Publisher for streaming data
Publishes sample e-commerce events to simulate real-time data
"""

import json
import time
import random
from datetime import datetime, timedelta
from google.cloud import pubsub_v1
import yaml

def load_config():
    """Load configuration from config.yaml"""
    with open('../config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def generate_sample_event():
    """Generate a sample e-commerce event"""

    event_types = ['purchase', 'page_view', 'add_to_cart', 'search', 'login']
    products = ['laptop', 'smartphone', 'headphones', 'tablet', 'camera']
    countries = ['UK', 'USA', 'Germany', 'France', 'Canada']

    # Generate realistic event
    event = {
        'event_id': f"evt_{random.randint(100000, 999999)}",
        'event_type': random.choice(event_types),
        'user_id': f"user_{random.randint(1000, 9999)}",
        'session_id': f"session_{random.randint(10000, 99999)}",
        'event_timestamp': datetime.utcnow().isoformat() + 'Z',
        'properties': {
            'product': random.choice(products),
            'price': round(random.uniform(50.0, 2000.0), 2),
            'quantity': random.randint(1, 5),
            'country': random.choice(countries),
            'device_type': random.choice(['mobile', 'desktop', 'tablet']),
            'page_url': f"/product/{random.choice(products)}",
            'referrer': random.choice(['google', 'facebook', 'direct', 'email'])
        },
        'data_source': 'ecommerce_app',
        'schema_version': '1.0'
    }

    return event

def publish_messages(project_id, topic_name, num_messages=100, delay_seconds=1):
    """Publish messages to Pub/Sub topic"""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    print(f"Publishing {num_messages} messages to {topic_path}")
    print(f"Delay between messages: {delay_seconds} seconds")
    print("-" * 50)

    published_count = 0

    try:
        for i in range(num_messages):
            # Generate sample event
            event = generate_sample_event()

            # Convert to JSON bytes
            message_data = json.dumps(event).encode('utf-8')

            # Add message attributes
            attributes = {
                'event_type': event['event_type'],
                'user_id': event['user_id'],
                'timestamp': event['event_timestamp']
            }

            # Publish message
            future = publisher.publish(topic_path, message_data, **attributes)
            message_id = future.result()  # Wait for publish to complete

            published_count += 1

            if published_count % 10 == 0:
                print(f"Published {published_count} messages...")

            # Print sample message
            if i < 3:
                print(f"Sample message {i+1}:")
                print(json.dumps(event, indent=2))
                print("-" * 30)

            # Wait before next message
            time.sleep(delay_seconds)

    except KeyboardInterrupt:
        print(f"\nStopped by user. Published {published_count} messages.")
    except Exception as e:
        print(f"Error publishing message: {e}")

    print(f"Total messages published: {published_count}")

def publish_batch_messages(project_id, topic_name, batch_size=50, num_batches=5):
    """Publish messages in batches for higher throughput"""

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    print(f"Publishing {num_batches} batches of {batch_size} messages each")

    total_published = 0

    for batch_num in range(num_batches):
        print(f"Publishing batch {batch_num + 1}/{num_batches}...")

        futures = []

        for i in range(batch_size):
            event = generate_sample_event()
            message_data = json.dumps(event).encode('utf-8')

            attributes = {
                'event_type': event['event_type'],
                'batch_id': str(batch_num)
            }

            # Publish async
            future = publisher.publish(topic_path, message_data, **attributes)
            futures.append(future)

        # Wait for all messages in batch to be published
        for future in futures:
            future.result()
            total_published += 1

        print(f"Batch {batch_num + 1} completed. Total published: {total_published}")

        # Wait between batches
        time.sleep(2)

    print(f"All batches completed. Total messages: {total_published}")

def main():
    """Main function"""
    config = load_config()
    project_id = config['project']['id']
    topic_name = config['pubsub']['input_topic'].split('/')[-1]  # Extract topic name

    print("=== Pub/Sub Publisher for Streaming Pipeline ===")
    print(f"Project: {project_id}")
    print(f"Topic: {topic_name}")
    print()

    # Choose publishing mode
    mode = input("Choose mode (1=continuous, 2=batch, 3=single): ").strip()

    if mode == "1":
        # Continuous publishing
        num_messages = int(input("Number of messages (default 100): ") or "100")
        delay = float(input("Delay between messages in seconds (default 1.0): ") or "1.0")
        publish_messages(project_id, topic_name, num_messages, delay)

    elif mode == "2":
        # Batch publishing
        batch_size = int(input("Batch size (default 50): ") or "50")
        num_batches = int(input("Number of batches (default 5): ") or "5")
        publish_batch_messages(project_id, topic_name, batch_size, num_batches)

    elif mode == "3":
        # Single message test
        event = generate_sample_event()
        print("Sample event:")
        print(json.dumps(event, indent=2))

        if input("Publish this message? (y/N): ").lower() == 'y':
            publish_messages(project_id, topic_name, 1, 0)

    else:
        print("Invalid mode selected")

if __name__ == "__main__":
    main()