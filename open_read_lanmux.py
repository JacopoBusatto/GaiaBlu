import serial

class result_container:
    pass

# function per aprire la porta di lanmux (port='COM12', baudrate=9600).
def open_port():

    # apertura porta
    lanmux=serial.Serial(port='COM12', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

    lanmux.flushInput()
    
    return lanmux

def read_data(lanmux_port):

    data=lanmux_port.readline().decode("utf-8")
    
    print(data)
                
def close_port(lanmux_port):
    lanmux_port.close()
