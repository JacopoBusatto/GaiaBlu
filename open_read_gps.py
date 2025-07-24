import serial

class result_container:
    pass

# function per aprire la porta del gps (port='COM5', baudrate=4800).
def open_port():

    # apertura porta
    gps=serial.Serial(port='COM5', baudrate=4800, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

    gps.flushInput()
    
    return gps

def read_data(gps_port):

    data=gps_port.readline().decode("utf-8")
    
    print(data)
                
def close_port(gps_port):
    gps_port.close()
