# P1 Example

import P1

s = P1.Serial()

s.setPort("COM3")  # or /dev/tty...

# configure for 9600 7N1
s.setBaud(9600)
s.setParity("N")  # None
s.setBits(7)
s.setStopbits(1)

# init serial connection
s.open()

# if a packed is received read packed
if s.read():
	# saved datafields
	data = [s.used_offpeak,
	s.used_peak,
	s.produced_offpeak,
	s.produced_peak,
	s.power,
	s.tarif,
	s.gas]
	print(data)