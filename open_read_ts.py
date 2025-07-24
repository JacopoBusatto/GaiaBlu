import serial

class result_container:
    pass

# function per aprire la porta del gps (port='COM5', baudrate=4800).
def open_port():

    # apertura porta
    ts=serial.Serial(port='COM9', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

    ts.flushInput()
    
    return ts

def read_data(ts_port):

    data=ts_port.readline().decode("utf-8")
    
    print(data)
                
def close_port(ts_port):
    ts_port.close()
