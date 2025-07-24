from pyACS.acs import ACS as ACSParser
import serial
import sys
import numpy as np

class result_container:
    pass

# function per aprire la porta dell'acs (port='COM7', baudrate=115200).
# dev file is hard-coded : 'C:\Users\GOS\AC-9\CDsEABIRD\ac90185_pio.dev
def open_port():

    # apertura porta
    acs=serial.Serial(port='COM7', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=False, dsrdtr=False)

    # operazioni reset (non so se servono)
    if acs.is_open:
        acs.reset_input_buffer()
        acs.reset_output_buffer()
        if acs.in_waiting > 0:
            acs.read(acs.in_waiting)

    # lettura file dev ACS
    dev=ACSParser(r'C:\Users\GOS\AC-9\CDsEABIRD\ac90185_pio.dev')
    
    return acs,dev

def read_data(acs_port,dev):

    # array lettura dati binari
    data_block=bytearray()

    # operazioni reset
    acs_port.reset_input_buffer()
    acs_port.reset_output_buffer()
    if acs_port.in_waiting > 0:
        acs_port.read(acs_port.in_waiting)

    go_read=True
    while go_read:
        # legge dato
        data=acs_port.read(acs_port.in_waiting or 1)
        # appende dato binario all'array
        data_block.extend(data)

        frame=True
        while frame:
        
            frame, valid, data_block, unknown_bytes=dev.find_frame(data_block)
            print(valid)

            if unknown_bytes:
                print('unknown_bytes')
                
            if frame and valid:
                # se il frame di lettura e completo lo spacchetta traducendolo in ASCII
                count_data=dev.unpack_frame(frame)
                # calibra i dati da conteggi a calori di assorbimento
                cal_data=dev.calibrate_frame(count_data,get_external_temperature=True)

                print(cal_data)
                
                # controlla lunghezza dato binario e lo azzera se troppo lungo
                if len(data_block) > 16384:
                    data_block=bytearray()

                go_read=False

def close_port(acs_port):
    acs_port.close()
