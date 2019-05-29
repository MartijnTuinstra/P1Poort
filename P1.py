import sys
import datetime
import re
import serial
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s\t- %(message)s')
logger = logging.getLogger(__name__)


class Serial():
    def __init__(self, config=None):
        self.used_offpeak = 0
        self.used_peak = 0
        self.produced_offpeak = 0
        self.produced_peak = 0
        self.power = 0
        self.tarif = 0
        self.gas = {}

        if config is not None:
            self.setParity(config.parity)
            self.setBits(config.bits)
            self.setBaud(config.baud)
            self.setPort(config.port)
            self.setStopbits(config.stopbits)

            self.open()

    def setParity(self, parity):
        self.parity = parity
    def setBaud(self, baud):
        self.baud = baud
    def setBits(self, bits):
        self.bits = bits
    def setPort(self, port):
        self.port = port
    def setStopbits(self, bits):
        self.stopbits = bits

    def open(self):
        self.s = serial.Serial(self.port, self.baud, parity=self.parity, bytesize=self.bits, stopbits=self.stopbits)
        logger.info("P1 Serial Init")

        # If it is open, close it
        if(self.s.isOpen() is True):
            self.s.close()
        self.s.open()

        # Check if serial port is opened
        if(self.s.isOpen() is False):
            logger.error("Could not open serial port ("+uart_port+"@"+str(baud_rate)+" "+self.bits+self.parity+self.stopbits+")")
            self.s.close()
            return None

    def read(self, raw=False):
        if self.s.inWaiting() > 10:
            # there is data in the buffer
            lines = []
            # read and store until a line with a ! as first character
            while True:
                lines.append(self.s.readline())
                if b'!' in lines[-1]:
                    break

            msg = b''.join(lines).decode("ascii")

            if raw:
                return msg

            self.decode(msg)

            return 1  # Got Message
        else:
            return 0  # No Message

    def decode(self, msg):
        used_peak = re.search(r'(?m)^1-0:1\.8\.1\(([\d.]*)\*kWh\)', msg)
        used_offpeak = re.search(r'(?m)^1-0:1\.8\.2\(([\d.]*)\*kWh\)', msg)
        produced_peak = re.search(r'(?m)^1-0:2\.8\.1\(([\d.]*)\*kWh\)', msg)
        produced_offpeak = re.search(r'(?m)^1-0:2\.8\.2\(([\d.]*)\*kWh\)', msg)

        current_use = re.search(r'(?m)^1-0:1\.7\.0\(([\d.]*)\*kW\)', msg)
        current_produce = re.search(r'(?m)^1-0:2\.7\.0\(([\d.]*)\*kW\)', msg)

        tarif = re.search(r'(?m)^0-0:96\.14\.0\(([\d.]*)\)', msg)

        gas = re.search(r'(?m)^0-1:24\.3\.0\((\d{2})(\d{2})(\d{2})(\d{2})\d{4}\)(?:\([\d\w\-\:\.]*\)){5}[\r\n]{1,2}\(([\d\.]*)\)', msg)

        if used_peak is not None:
            self.used_offpeak = float(used_peak.group(1))
        if used_offpeak is not None:
            self.used_peak = float(used_offpeak.group(1))
        if produced_peak is not None:
            self.produced_offpeak = float(produced_peak.group(1))
        if produced_offpeak is not None:
            self.produced_peak = float(produced_offpeak.group(1))

        if current_use is not None:
            self.power = float(current_use.group(1))
        if current_produce is not None:
            self.power -= float(current_produce.group(1))

        if tarif is not None:
            self.tarif = tarif.group(1)

        if gas is not None:
            self.gas = {"dt": datetime.datetime(int("20"+gas.group(1)), int(gas.group(2)), int(gas.group(3)), int(gas.group(4)), 0, 0), "gas": float(gas.group(5))}
