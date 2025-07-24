from open_read_acs import open_port, close_port
from modules.config import INITIAL_SLEEP, MAX_TRIES, TRY_DELAY
import time

def get_acs_data():
    try:
        acs_port, dev = open_port()
        time.sleep(INITIAL_SLEEP)

        data_block = bytearray()
        acs_port.reset_input_buffer()
        acs_port.reset_output_buffer()

        for _ in range(MAX_TRIES):
            data = acs_port.read(acs_port.in_waiting or 1)
            data_block.extend(data)

            frame, valid, data_block, unknown_bytes = dev.find_frame(data_block)

            if frame and valid:
                count_data = dev.unpack_frame(frame)
                cal_data = dev.calibrate_frame(count_data, get_external_temperature=True)

                result = {}

                # C_lambda (attenuazione)
                for lam, val in zip(dev.lambda_c, cal_data.c):
                    result[f"C_{lam:.1f}"] = float(val)

                # A_lambda (assorbimento)
                for lam, val in zip(dev.lambda_a, cal_data.a):
                    result[f"A_{lam:.1f}"] = float(val)

                # Temperature
                result["INT_TEMP"] = float(cal_data.internal_temperature)
                result["EXT_TEMP"] = float(cal_data.external_temperature)

                return result

            time.sleep(TRY_DELAY)

        print("[acs] Nessun frame valido trovato.")
        return {}
    except Exception as e:
        print(f"[acs] Errore lettura: {e}")
        return {}
    finally:
        try:
            close_port(acs_port)
        except:
            pass
