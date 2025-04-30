import pika
import sys

def send_write_message(line):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='broadcast_ex', exchange_type='fanout')

    channel.basic_publish(
        exchange='broadcast_ex',
        routing_key='',
        body=f'write|{line}',
        properties=None
    )

    connection.close()


def main():
    while True:
        cmd = input("Commands: [write, exit] > ").strip().lower()
        if cmd == 'exit':
            break
        elif cmd == 'write':
            line = input("Enter the line to write: ").strip()
            if not line:
                continue
            send_write_message(line)
        else:
            print("Unknown command. Please try again.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(1)