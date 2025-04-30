import pika
import os
import threading
import sys


def write_line(replica_id, line):
    directory = f'data/replica_{replica_id}'
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, 'data.txt')
    with open(filepath, 'a') as f:
        f.write(line + '\n')

def read_last_line(replica_id):
    filepath = f'data/replica_{replica_id}/data.txt'
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            return lines[-1].strip() if lines else "EMPTY"
    except FileNotFoundError:
        return "NOT FOUND"

def read_all_lines(replica_id):
    filepath = f'data/replica_{replica_id}/data.txt'
    try:
        with open(filepath, 'r') as f:
            return [ line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def send_to_queue(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=False)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

def handle_direct(replica_id):
    def callback(ch, method, properties, body):
        message = body.decode()
        print(f"[Replica {replica_id}] Received direct message: {message}")
        if message.startswith('write|'):
            _, line = message.split('|', 1)
            write_line(replica_id, line)
            print(f"[Replica {replica_id}] Wrote line: {line}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    queue_name = f'replica_{replica_id}'
    channel.queue_declare(queue=queue_name, durable=False,auto_delete=True,exclusive=True)
    print(f"[Replica {replica_id}] Listening for direct messages on queue '{queue_name}'...")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def handle_broadcast(replica_id):
    def callback(ch, method, properties, body):
        message = body.decode()
        print(f"[Replica {replica_id}] Received direct message: {message}")
        if message.startswith('write|'):
            _, line = message.split('|', 1)
            write_line(replica_id, line)
            print(f"[Replica {replica_id}] Wrote line: {line}")
        if message == 'read_last':
            response = read_last_line(replica_id)
            send_to_queue('client_reader', response)
            print(f"[Replica {replica_id}] Sent last line: {response}")
        elif message == 'read_all':
            lines = read_all_lines(replica_id)
            for line in lines:
                send_to_queue('client_reader_v2', line)
                print(f"[Replica {replica_id}] Sent line to majority queue: {line}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='broadcast_ex', exchange_type='fanout')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='broadcast_ex', queue=queue_name)

    print(f"[Replica {replica_id}] Listening for broadcasts on exchange 'broadcast_ex'...")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def main():
    if len(sys.argv) != 2:
        print("Usage: python replica.py <replica_id>")
        print("Usage: python replica.py <replica_id>")
        sys.exit(1)
    replica_id = sys.argv[1]
    print(f"Starting replica service for replica ID: {replica_id}")
    threading.Thread(target=handle_direct, args=(replica_id,)).start()
    threading.Thread(target=handle_broadcast, args=(replica_id,)).start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Service interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")





# def handle_queue(queue_name, replica_id, respond=False):
#     print(f"[Replica {replica_id}] Processing message...")
#     def callback(ch, method, properties, body):
#         message = body.decode()
#         # logger.info(f'Received message from  {queue_name}: {message}')
#         print(f'Received message from  {queue_name}: {message}')
#         if message.startswith('write|'):
#             _, line = message.split('|', 1)
#             write_line(replica_id, line)
#             # logger.info(f'written line to replica {replica_id} :{line}')
#             print(f'written line to replica {replica_id} :{line}')
#         elif message == 'read_last' and respond:
#             response = read_last_line(replica_id)
#             send_to_queue('client_reader', response)
#             # logger.info(f'Read last line from replica {replica_id}: {response}')
#             print(f'Read last line from replica {replica_id}: {response}')
#         elif message == 'read_all' and respond:
#             lines = read_all_lines(replica_id)
#             # logger.info(f'Read all lines from replica {replica_id}:')
#             print(f'Read all lines from replica {replica_id}:')
#             for line in lines:
#                 # logger.info(f'> {line}')
#                 print(f'> {line}')
#                 send_to_queue('client_reader_v2', line)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()
#     channel.queue_declare(queue=queue_name, durable=False)
#     # logger.debug(f"Declared queue: {queue_name}")
#     print(f"Declared queue: {queue_name}")
#     channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     # logger.info(f"Waiting for messages in {queue_name}. To exit press CTRL+C")
#     print(f"Waiting for messages in {queue_name}. To exit press CTRL+C")
#     channel.start_consuming()
