import psutil
import time

def get_analyser():

    first_reading = psutil.net_io_counters()
    time.sleep(60)  # Wait for a short interval to get a new reading
    second_reading = psutil.net_io_counters()
    return {
        "bytes_sent": second_reading.bytes_sent - first_reading.bytes_sent,
        "bytes_recv": second_reading.bytes_recv - first_reading.bytes_recv,
        "packets_sent": second_reading.packets_sent - first_reading.packets_sent,
        "packets_recv": second_reading.packets_recv - first_reading.packets_recv
    }
if __name__ == "__main__":
    print(get_analyser())