import pika
import os
from collections import defaultdict
from log_utils import setup_logging

logger = setup_logging('client_reader')

def get_majority_lines(responses):
    logger.debug(f"Processing responses: {responses}")
    line_counts = defaultdict(int)
    for response in responses:
        lines = response.split("\n")
        for line in lines:
            if line.strip():
                line_counts[line] += 1

    majority = []
    for line, count in line_counts.items():
        if count >= 2:  # Au moins 2/3 replicas d'accord
            majority.append(line)
    logger.debug(f"Majority consensus reached for {len(majority)} lines")
    return majority

def main():
    logger.info("Starting client reader service")
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    responses = []
    for i in range(1, 4):
        callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue
        logger.debug(f"Created callback queue for replica {i}: {callback_queue}")
        
        channel.basic_publish(
            exchange='',
            routing_key=f"read_queue_{i}",
            body="READ_ALL",
            properties=pika.BasicProperties(reply_to=callback_queue))
        logger.info(f"Sent READ_ALL request to replica {i}")

        method, _, body = channel.consume(callback_queue, auto_ack=True)
        response = body.decode()
        logger.debug(f"Received response from replica {i}: {response}")
        responses.append(response)

    majority_lines = get_majority_lines(responses)
    logger.info("Consensus reached, printing results")
    for line in majority_lines:
        print(line)
        logger.debug(f"Consensus line: {line}")

    connection.close()
    logger.info("Client reader service completed")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)