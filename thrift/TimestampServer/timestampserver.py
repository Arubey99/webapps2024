import thriftpy2
from thriftpy2.rpc import make_server

timestamp_thrift = thriftpy2.load("thrift/timestamp.thrift", module_name="timestamp_thrift")

class TimeStampingHandler:
    def getCurrentTimestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    server = make_server(timestamp_thrift.TimeStampingService, TimeStampingHandler(), '127.0.0.1', 9090)
    print("serving...")
    server.serve()

if __name__ == '__main__':
    main()
