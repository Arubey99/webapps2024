import thriftpy2
from thriftpy2.rpc import make_client

timestamp_thrift = thriftpy2.load("thrift/timestamp.thrift", module_name="timestamp_thrift")

def get_current_timestamp():
    client = make_client(timestamp_thrift.TimeStampingService, '127.0.0.1', 9090)
    timestamp = client.getCurrentTimestamp()
    client.close()
    return timestamp

if __name__ == '__main__':
    print("Current Timestamp: ", get_current_timestamp())
