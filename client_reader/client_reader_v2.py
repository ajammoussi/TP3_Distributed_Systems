import pika
import time
from collections import Counter

def send_read_all_request():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='broadcast_ex', exchange_type='fanout')
    channel.basic_publish(
        exchange='broadcast_ex',
        routing_key='',
        body='read_all'
    )
    connection.close()

def collect_lines(timeout=3):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='client_reader_v2')

    lines = []

    def callback(ch, method, properties, body):
        line = body.decode()
        lines.append(line)

    channel.basic_consume(queue='client_reader_v2', on_message_callback=callback, auto_ack=True)

    print("[ClientReaderV2] Waiting for lines...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        connection.process_data_events(time_limit=0.1)

    connection.close()
    return lines

def majority_vote(lines):
    count = Counter(lines)
    majority_lines = [line for line, freq in count.items() if freq >= 2]
    return majority_lines

if __name__ == "__main__":
    send_read_all_request()
    time.sleep(0.5)  
    all_lines = collect_lines(timeout=3)
    
    print(f"\n[ClientReaderV2] Received {len(all_lines)} lines.")
    majority_lines = majority_vote(all_lines)

    print("\nLines that appear in the majority of replicas:")
    for line in majority_lines:
        print(f" > {line}")
