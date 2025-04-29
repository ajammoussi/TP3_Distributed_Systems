import pika
import os
import sys
from log_utils import setup_logging

logger = setup_logging('client_writer')

def main():
    logger.info("Starting client writer service")
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    
    channel.queue_declare(queue=os.environ['QUEUE_WRITE'], durable=True)
    logger.debug(f"Declared queue: {os.environ['QUEUE_WRITE']}")

    messages = [
        "1 Texte message1",
        "2 Texte message2",
        "3 Texte message3",
        "4 Texte message4"
    ]

    for msg in messages:
        channel.basic_publish(
            exchange='',
            routing_key=os.environ['QUEUE_WRITE'],
            body=msg,
            properties=pika.BasicProperties(delivery_mode=2)  # Persistant
        )
        logger.info(f"Sent message: {msg}")

    logger.info("All messages sent successfully")
    connection.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)