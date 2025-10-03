# 🚀 Kafka Tutorial: Real-Time Streaming for Kpop Demon Hunter Merchandise

This tutorial demonstrates how to use **Apache Kafka** (via Redpanda to make it a bit easier) for real-time streaming of customer orders. 


## 📋 Prerequisites

- Docker and Docker Compose installed
- Python environment with Kafka libraries
- Basic understanding of streaming concepts

## 🏗️ Step 1: Setup Kafka Infrastructure

### 1.1 Start Kafka with Redpanda

```bash
# Start the Kafka infrastructure
docker compose up -d

# Check if containers are running
docker compose ps
```

**What this creates:**
- **Redpanda**: Kafka-compatible message broker (don't worry about it, it just make it easier)
- **Connect**: Kafka Connect for Snowflake integration

# 1.2 create a py file publish_data.py

"""
publish_data.py
"""
#!/usr/bin/env python3
import os
import logging
import sys
import confluent_kafka
from kafka.admin import KafkaAdminClient, NewTopic
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Configuration from environment variables
kafka_brokers = os.getenv("REDPANDA_BROKERS", "127.0.0.1:19092")
topic_name = os.getenv("KAFKA_TOPIC", "kpop_merchandise_orders")

def create_topic():
    """Create Kafka topic if it doesn't exist"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=kafka_brokers, 
            client_id='kpop_merchandise_publisher'
        )
        topic_metadata = admin_client.list_topics()
        
        if topic_name not in topic_metadata:
            logging.info(f"📝 Creating topic: {topic_name}")
            topic = NewTopic(
                name=topic_name, 
                num_partitions=10, 
                replication_factor=1
            )
            admin_client.create_topics(new_topics=[topic], validate_only=False)
            logging.info(f"✅ Topic '{topic_name}' created successfully")
        else:
            logging.info(f"✅ Topic '{topic_name}' already exists")
            
    except Exception as e:
        logging.error(f"❌ Error creating topic: {e}")
        raise

def get_kafka_producer():
    """Create and configure Kafka producer"""
    logging.info(f"🔌 Connecting to Kafka brokers: {kafka_brokers}")
    
    config = {
        'bootstrap.servers': kafka_brokers,
        'client.id': 'kpop_merchandise_producer',
        'acks': 'all',  # Wait for all replicas to acknowledge
        'retries': 3,   # Retry failed messages
        'retry.backoff.ms': 100,
        'compression.type': 'snappy',  # Compress messages for efficiency
        'batch.size': 16384,  # Batch messages for better throughput
        'linger.ms': 10,  # Wait up to 10ms to batch messages
    }
    
    return confluent_kafka.Producer(**config)

def publish_message(producer, message):
    """Publish a single message to Kafka with error handling"""
    try:
        # Produce message to topic
        producer.produce(
            topic_name, 
            value=bytes(message, encoding='utf8'),
            callback=delivery_callback
        )
        return True
        
    except BufferError as e:
        logging.warning(f"⚠️  Producer buffer full, flushing...")
        producer.flush()
        # Retry after flush
        producer.produce(topic_name, value=bytes(message, encoding='utf8'))
        return True
        
    except Exception as e:
        logging.error(f"❌ Error publishing message: {e}")
        return False

def delivery_callback(err, msg):
    """Callback function for message delivery confirmation"""
    if err is not None:
        logging.error(f"❌ Message delivery failed: {err}")
    else:
        logging.debug(f"✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def main():
    """Main publishing function"""
    print(f"🚀 Starting Kafka Publisher for Kpop Demon Hunter Merchandise Orders")
    print(f"📊 Topic: {topic_name}")
    print(f"🔌 Brokers: {kafka_brokers}")
    print("=" * 60)
    
    try:
        # Create topic if needed
        create_topic()
        
        # Create producer
        producer = get_kafka_producer()
        
        # Statistics
        messages_published = 0
        messages_failed = 0
        
        print(f"📡 Publishing messages... (Press Ctrl+C to stop)")
        
        # Process messages from stdin
        for message in sys.stdin:
            if message != '\n':
                # Clean the message
                message = message.strip()
                if not message:
                    continue
                
                # Publish message with retry logic
                failed = True
                retry_count = 0
                max_retries = 3
                
                while failed and retry_count < max_retries:
                    if publish_message(producer, message):
                        messages_published += 1
                        failed = False
                        
                        # Log progress every 100 messages
                        if messages_published % 100 == 0:
                            print(f"📊 Published {messages_published} messages...")
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            logging.warning(f"⚠️  Retry {retry_count}/{max_retries} for message")
                        else:
                            messages_failed += 1
                            logging.error(f"❌ Failed to publish message after {max_retries} retries")
                            failed = False
            else:
                break
        
        # Flush any remaining messages
        print(f"🔄 Flushing remaining messages...")
        producer.flush(timeout=10)
        
        # Final statistics
        print(f"\n📊 Publishing Complete!")
        print(f"   ✅ Messages published: {messages_published}")
        print(f"   ❌ Messages failed: {messages_failed}")
        print(f"   📈 Success rate: {(messages_published/(messages_published+messages_failed)*100):.1f}%")
        
        if messages_failed > 0:
            print(f"\n⚠️  Some messages failed to publish. Check Kafka broker status.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Publisher stopped by user")
        producer.flush(timeout=5)
        print(f"📊 Final stats: {messages_published} published, {messages_failed} failed")
        
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


### 1.3 Update you .env. 

After your snowflake setting add some kafka settings

```env
# Existing Snowflake settings
SNOWFLAKE_ACCOUNT=YOUR_ACCOUNT_IDENTIFIER
SNOWFLAKE_USER=INGEST
PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE

# New Kafka settings
REDPANDA_BROKERS=127.0.0.1:19092
KAFKA_TOPIC=kpop_merchandise_orders
KAFKA_CONSUMER_GROUP=kpop_merchandise_consumer
```

## 🐍 Step 2: Install Required Packages

Add these to your `environment.yml`:

```yaml
dependencies:
  - kafka-python=2.0.2
  - confluent-kafka=2.3.0
  - python-confluent-kafka
```

Or install directly:
```bash
pip install kafka-python confluent-kafka
```

## 🚀 Step 3: Test Kafka Publishing

### 3.1 Basic Publishing Test
## First create the publishn py file, like you have done for consume

import os
import logging
import sys
import confluent_kafka
from kafka.admin import KafkaAdminClient, NewTopic
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Configuration from environment variables
kafka_brokers = os.getenv("REDPANDA_BROKERS", "127.0.0.1:19092")
topic_name = os.getenv("KAFKA_TOPIC", "kpop_merchandise_orders")

def create_topic():
    """Create Kafka topic if it doesn't exist"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=kafka_brokers, 
            client_id='kpop_merchandise_publisher'
        )
        topic_metadata = admin_client.list_topics()
        
        if topic_name not in topic_metadata:
            logging.info(f"📝 Creating topic: {topic_name}")
            topic = NewTopic(
                name=topic_name, 
                num_partitions=10, 
                replication_factor=1
            )
            admin_client.create_topics(new_topics=[topic], validate_only=False)
            logging.info(f"✅ Topic '{topic_name}' created successfully")
        else:
            logging.info(f"✅ Topic '{topic_name}' already exists")
            
    except Exception as e:
        logging.error(f"❌ Error creating topic: {e}")
        raise

def get_kafka_producer():
    """Create and configure Kafka producer"""
    logging.info(f"🔌 Connecting to Kafka brokers: {kafka_brokers}")
    
    config = {
        'bootstrap.servers': kafka_brokers,
        'client.id': 'kpop_merchandise_producer',
        'acks': 'all',  # Wait for all replicas to acknowledge
        'retries': 3,   # Retry failed messages
        'retry.backoff.ms': 100,
        'compression.type': 'snappy',  # Compress messages for efficiency
        'batch.size': 16384,  # Batch messages for better throughput
        'linger.ms': 10,  # Wait up to 10ms to batch messages
    }
    
    return confluent_kafka.Producer(**config)

def publish_message(producer, message):
    """Publish a single message to Kafka with error handling"""
    try:
        # Produce message to topic
        producer.produce(
            topic_name, 
            value=bytes(message, encoding='utf8'),
            callback=delivery_callback
        )
        return True
        
    except BufferError as e:
        logging.warning(f"⚠️  Producer buffer full, flushing...")
        producer.flush()
        # Retry after flush
        producer.produce(topic_name, value=bytes(message, encoding='utf8'))
        return True
        
    except Exception as e:
        logging.error(f"❌ Error publishing message: {e}")
        return False

def delivery_callback(err, msg):
    """Callback function for message delivery confirmation"""
    if err is not None:
        logging.error(f"❌ Message delivery failed: {err}")
    else:
        logging.debug(f"✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def main():
    """Main publishing function"""
    print(f"🚀 Starting Kafka Publisher for Kpop Demon Hunter Merchandise Orders")
    print(f"📊 Topic: {topic_name}")
    print(f"🔌 Brokers: {kafka_brokers}")
    print("=" * 60)
    
    try:
        # Create topic if needed
        create_topic()
        
        # Create producer
        producer = get_kafka_producer()
        
        # Statistics
        messages_published = 0
        messages_failed = 0
        
        print(f"📡 Publishing messages... (Press Ctrl+C to stop)")
        
        # Process messages from stdin
        for message in sys.stdin:
            if message != '\n':
                # Clean the message
                message = message.strip()
                if not message:
                    continue
                
                # Publish message with retry logic
                failed = True
                retry_count = 0
                max_retries = 3
                
                while failed and retry_count < max_retries:
                    if publish_message(producer, message):
                        messages_published += 1
                        failed = False
                        
                        # Log progress every 100 messages
                        if messages_published % 100 == 0:
                            print(f"📊 Published {messages_published} messages...")
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            logging.warning(f"⚠️  Retry {retry_count}/{max_retries} for message")
                        else:
                            messages_failed += 1
                            logging.error(f"❌ Failed to publish message after {max_retries} retries")
                            failed = False
            else:
                break
        
        # Flush any remaining messages
        print(f"🔄 Flushing remaining messages...")
        producer.flush(timeout=10)
        
        # Final statistics
        print(f"\n📊 Publishing Complete!")
        print(f"   ✅ Messages published: {messages_published}")
        print(f"   ❌ Messages failed: {messages_failed}")
        print(f"   📈 Success rate: {(messages_published/(messages_published+messages_failed)*100):.1f}%")
        
        if messages_failed > 0:
            print(f"\n⚠️  Some messages failed to publish. Check Kafka broker status.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Publisher stopped by user")
        producer.flush(timeout=5)
        print(f"📊 Final stats: {messages_published} published, {messages_failed} failed")
        
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()





```bash
# Set the topic name
export KAFKA_TOPIC=kpop_merchandise_orders

# Publish 1 test message
python data_generator.py 1 | python publish_data.py
```

**Expected Output:**
```
🚀 Starting Kafka Publisher for Kpop Demon Hunter Merchandise Orders
📊 Topic: kpop_merchandise_orders
🔌 Brokers: 127.0.0.1:19092
📝 Creating topic: kpop_merchandise_orders
✅ Topic 'kpop_merchandise_orders' created successfully
🔌 Connecting to Kafka brokers: 127.0.0.1:19092
📡 Publishing messages... (Press Ctrl+C to stop)
📊 Published 1 messages...
📊 Publishing Complete!
   ✅ Messages published: 1
   ❌ Messages failed: 0
   📈 Success rate: 100.0%
```

### 3.2 Verify in Web Console

1. Go to **http://localhost:8080**
2. Click on **Topics** in the sidebar
3. Find `kpop_merchandise_orders` topic
4. Click on it to see message details
(it will not work if docker is not install properly)

## 📡 Step 4: Test Kafka Consumption

### 4.1 Start a Consumer

```bash
# In a new terminal, start consuming messages
python consume_data.py
```

**Expected Output:**
```
🚀 Starting Kafka Consumer for Kpop Demon Hunter Merchandise Orders
📊 Topic: kpop_merchandise_orders
👥 Consumer Group: kpop_merchandise_consumer
🔌 Brokers: 127.0.0.1:19092
📡 Waiting for messages... (Press Ctrl+C to stop)
```

### 4.2 Publish Messages (in another terminal)

```bash
# Publish 5 messages
python data_generator.py 5 | python publish_data.py
```

**You should see the consumer display:**
```
📦 Order #1
   🆔 Transaction ID: 123e4567-e89b-12d3-a456-426614174000
   🛍️  Product: Kpop Demon Hunter T-Shirt
   👤 Customer: John Smith
   📧 Email: john.smith@email.com
   🕐 Purchase Time: 2024-01-15T10:30:00.000000
   🏠 Address: 123 Main St, New York, NY 10001
   📍 Partition: 0, Offset: 0
```

## 🎮 Step 5: Advanced Testing

### 5.1 High-Volume Publishing

```bash
# Publish 1000 messages
python data_generator.py 1000 | python publish_data.py
```

### 5.2 Multiple Consumers

```bash
# Terminal 1: Start consumer 1
python consume_data.py

# Terminal 2: Start consumer 2 (in another terminal)
export KAFKA_CONSUMER_GROUP=kpop_merchandise_consumer_2
python consume_data.py

# Terminal 3: Publish messages
python data_generator.py 100 | python publish_data.py
```

**What happens:**
- Messages are distributed between consumers
- Each consumer processes different messages
- Kafka handles load balancing automatically

### 5.3 Partition Testing

```bash
# Publish messages with specific keys (for partition testing)
python data_generator.py 10 | python publish_data.py
```

## 📊 Step 6: Monitor Kafka Performance

### 6.1 Web Console Monitoring

Visit **http://localhost:8080** to see:

- **Topics**: Message counts, partition distribution
- **Consumers**: Consumer group status, lag monitoring
- **Brokers**: Resource usage, performance metrics
- **Messages**: Real-time message flow

### 6.2 Command Line Monitoring

```bash
# Check container status
docker compose ps

# View logs
docker compose logs redpanda-0

# Check topic details
docker compose exec redpanda-0 rpk topic list
```

## 🔧 Step 7: Understanding Kafka Concepts

### 7.1 Key Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Topic** | Category for messages | `kpop_merchandise_orders` |
| **Partition** | Subdivision of topic | 10 partitions for load balancing |
| **Producer** | Sends messages | `publish_data.py` |
| **Consumer** | Receives messages | `consume_data.py` |
| **Consumer Group** | Set of consumers | `kpop_merchandise_consumer` |
| **Offset** | Message position | Each message has unique offset |

### 7.2 Message Flow

```
Data Generator → Producer → Kafka Topic → Consumer → Processing
     ↓              ↓           ↓           ↓
  JSON Data    Message    Partition    Real-time
  Records      Publishing  Distribution  Processing
```

### 7.3 Reliability Features

- **Message Persistence**: Messages stored on disk
- **Replication**: Multiple copies for fault tolerance
- **Offset Tracking**: Resume from last processed message
- **Error Handling**: Retry failed messages

## 🎯 Step 8: Business Use Cases

### 8.1 Real-Time Analytics

```python
# Example: Real-time order processing
def process_order(message):
    order = json.loads(message)
    
    # Update inventory
    update_inventory(order['item'])
    
    # Send confirmation email
    send_email(order['email'])
    
    # Update customer profile
    update_customer_profile(order)
```

### 8.2 Event-Driven Architecture

```python
# Example: Trigger downstream processes
def handle_order_event(message):
    order = json.loads(message)
    
    if order['item'].startswith('Kpop Demon Hunter'):
        # Trigger merchandise fulfillment
        trigger_fulfillment(order)
    
    if order['amount'] > 100:
        # Trigger VIP customer process
        trigger_vip_process(order)
```

## 🚨 Step 9: Troubleshooting

### 9.1 Common Issues

**"Connection refused"**
```bash
# Check if containers are running
docker compose ps

# Restart if needed
docker compose restart
```

**"Topic not found"**
```bash
# Check topic exists
docker compose exec redpanda-0 rpk topic list

# Create topic manually if needed
docker compose exec redpanda-0 rpk topic create kpop_merchandise_orders --partitions 10
```

**"Consumer not receiving messages"**
- Check consumer group status in web console
- Verify topic has messages
- Check consumer configuration

### 9.2 Debug Commands

```bash
# View all topics
docker compose exec redpanda-0 rpk topic list

# View topic details
docker compose exec redpanda-0 rpk topic describe kpop_merchandise_orders

# View consumer groups
docker compose exec redpanda-0 rpk group list

# View messages in topic
docker compose exec redpanda-0 rpk topic consume kpop_merchandise_orders --num 10
```

## 🎯 Step 10: Performance Optimization

### 10.1 Producer Optimization

```python
# Optimize for throughput
config = {
    'batch.size': 32768,      # Larger batches
    'linger.ms': 50,          # Wait to batch messages
    'compression.type': 'snappy',  # Compress messages
    'acks': '1',              # Faster acknowledgment
}
```

### 10.2 Consumer Optimization

```python
# Optimize for throughput
config = {
    'fetch.min.bytes': 1024,     # Fetch more data at once
    'fetch.max.wait.ms': 500,    # Wait for batch
    'max.partition.fetch.bytes': 1048576,  # Larger fetch size
}
```

## 🚀 Step 11: Integration with Snowflake

### 11.1 Kafka Connect Setup

The Docker setup includes Kafka Connect with Snowflake connector:

```bash
# Check connect status
docker compose logs connect

# Access connect UI
# http://localhost:8083
```

### 11.2 Snowflake Sink Configuration

```json
{
  "name": "snowflake-sink",
  "config": {
    "connector.class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
    "topics": "kpop_merchandise_orders",
    "snowflake.topic2table.map": "kpop_merchandise_orders:CLIENT_SUPPORT_ORDERS",
    "snowflake.url.name": "YOUR_SNOWFLAKE_URL",
    "snowflake.user.name": "INGEST",
    "snowflake.private.key": "YOUR_PRIVATE_KEY",
    "snowflake.database.name": "INGEST",
    "snowflake.schema.name": "INGEST"
  }
}
```

## 🎉 Key Takeaways

1. **Kafka enables real-time streaming** - not batch processing
2. **Partitions provide scalability** - more partitions = more , like qu
3. **Consumer groups enable load balancing** - distribute work across consumers
4. **Message reliability** - Kafka guarantees message delivery
5. **Web console is essential** - monitor and debug your streams

## 🚀 Next Steps

- **Scale up**: Process 10K+ messages per second
- **Add monitoring**: Set up alerts for consumer lag
- **Integrate**: Connect to Snowflake via Kafka Connect
- **Optimize**: Tune for your specific use case
- **Deploy**: Move to production Kafka cluster

## 📚 Additional Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Redpanda Console](https://docs.redpanda.com/console/)
- [Kafka Connect](https://docs.confluent.io/platform/current/connect/index.html)
- [Snowflake Kafka Connector](https://docs.snowflake.com/en/user-guide/kafka-connector)

---

**🎉 Congratulations! I am impressed. You made it. you can have fun with kafka and chekc the monitoring console** 
