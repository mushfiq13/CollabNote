import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer

from app.mongodb import connect_to_mongodb, close_mongodb_connection, get_mongodb

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "activity_logs")
KAFKA_GROUP_ID = "log_consumer_group"

async def consume_logs():
    # Connect to MongoDB
    await connect_to_mongodb()
    mongodb = get_mongodb()

    # Create Kafka consumer
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest', # Start from beginning if no offset is committed
        enable_auto_commit=True
    )

    await consumer.start()
    print(f"Kafka consumer started. Listening to topic: {KAFKA_TOPIC}")

    try:
        async for message in consumer:
            log_data = message.value

            print(f"Recieved message: {log_data}")

            # Convert timestamp string back to datetime
            if "timestamp" in log_data and isinstance(log_data["timestamp"], str):
                log_data["timestamp"] = datetime.fromisoformat(log_data["timestamp"])

            # Save to MongoDB
            result = await mongodb.logs.insert_one(log_data)
            print(f"Log saved to MongoDB with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error consuming logs: {e}")
    finally:
        await consumer.stop()
        await close_mongodb_connection()
        print("Kafka consumer stopped.")

if __name__ == "__main__":
    print("Starting log consumer...")
    asyncio.run(consume_logs())
