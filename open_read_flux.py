import serial
import sys

class result_container:
    pass

# function per aprire la porta del flussimetro (port='COM8', baudrate=9600).
def open_port():

    # apertura porta
    flux=serial.Serial(port='COM8', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

    flux.flushInput()
    
    return flux

def read_data(flux_port):
    
    data=flux_port.readline().decode("utf-8")
                                     
    print(data)

                
def close_port(flux_port):
    flux_port.close()
