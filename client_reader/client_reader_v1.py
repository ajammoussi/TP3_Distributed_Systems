import pika
import time

def send_read_last_request():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='broadcast_ex', exchange_type='fanout')
    channel.basic_publish(
        exchange='broadcast_ex',
        routing_key='', 
        body='read_last',
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()


# TASK 4 asking for all responses from replicas
def listen_for_responses(timeout=3):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='client_reader')

    messages = []

    def callback(ch, method, properties, body):
        text = body.decode()
        messages.append(text)
        print(f"[ClientReader] Received from replica: {text}")

    channel.basic_consume(queue='client_reader', on_message_callback=callback, auto_ack=True)

    print("[ClientReader] Waiting for responses...")
    start = time.time()
    while time.time() - start < timeout:
        connection.process_data_events(time_limit=0.1)
    connection.close()
    return messages


#TASK 5: asking for the first response only 
def listen_for_first_response(timeout=3):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='client_reader')

    response = []

    def callback(ch, method, properties, body):
        response.append(body.decode())
        print(f"[ClientReader] First received: {response[0]}")
        channel.stop_consuming() 

    channel.basic_consume(queue='client_reader', on_message_callback=callback, auto_ack=True)
    print("[ClientReader] Waiting for first available response...")

    try:
        channel.start_consuming()
    except Exception:
        pass

    connection.close()
    return response


if __name__ == '__main__':
    send_read_last_request()
    time.sleep(0.5) 
    responses = listen_for_first_response(timeout=3)

    print(f"\n[ClientReader] Total responses received: {len(responses)}")
    if not responses:
        print("[ClientReader] No responses received. Are replicas running?")
