# P1 Example

import P1
import time

s = P1.Serial()

s.setPort("COM3")  # or /dev/tty...

# configure for 9600 7N1
s.setBaud(9600)
s.setParity("N")  # None
s.setBits(7)
s.setStopbits(1)

# init serial connection
s.open()

# wait Interval of messages
# to have capture message
time.sleep(10)

# if a packed is received read packed
if s.read():
    # saved datafields
    data = [s.used_offpeak,  # kWh
    s.used_peak,             # kWh
    s.produced_offpeak,      # kWh
    s.produced_peak,         # kWh
    s.power,                 # W
    s.tarif,                 # 1 offpeak, 2 peak
    s.gas]                   # date and m3
    print(data)
