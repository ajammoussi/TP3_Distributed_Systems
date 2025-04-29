import pika
import os
from log_utils import setup_logging

logger = setup_logging('replica')

def on_write_request(ch, method, props, body):
    line = body.decode()
    logger.info(f"Received write request: {line}")
    try:
        with open(f"data/replica_{os.environ['REPLICA_ID']}.txt", "a") as f:
            f.write(line + "\n")
        logger.debug(f"Successfully wrote line to replica {os.environ['REPLICA_ID']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error writing to file: {str(e)}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag)

def on_read_request(ch, method, props, body):
    request_type = body.decode()
    logger.info(f"Received read request: {request_type}")
    response = ""

    try:
        with open(f"data/replica_{os.environ['REPLICA_ID']}.txt", "r") as f:
            lines = f.readlines()
            if request_type == "READ_LAST":
                response = lines[-1] if lines else "EMPTY"
                logger.debug(f"READ_LAST response: {response}")
            elif request_type == "READ_ALL":
                response = "".join(lines) if lines else "EMPTY"
                logger.debug(f"READ_ALL response: {response}")
    except FileNotFoundError:
        logger.warning(f"Data file not found for replica {os.environ['REPLICA_ID']}")
        response = "EMPTY"
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}", exc_info=True)
        response = "ERROR"

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    logger.info(f"Starting replica {os.environ['REPLICA_ID']}")
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue=os.environ['QUEUE_WRITE'], durable=True)
    channel.queue_declare(queue=os.environ['QUEUE_READ'], durable=True)
    
    logger.debug(f"Declared queues: write={os.environ['QUEUE_WRITE']}, read={os.environ['QUEUE_READ']}")

    channel.basic_consume(queue=os.environ['QUEUE_WRITE'], on_message_callback=on_write_request)
    channel.basic_consume(queue=os.environ['QUEUE_READ'], on_message_callback=on_read_request)

    logger.info(f"Replica {os.environ['REPLICA_ID']} started. Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)