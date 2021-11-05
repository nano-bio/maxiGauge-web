#!/usr/bin/env python
# -*- encoding: UTF8 -*-

# Author: Philipp Klaus, philipp.l.klaus AT web.de

# This file is part of PfeifferVacuum.py.
#
# PfeifferVacuum.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PfeifferVacuum.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PfeifferVacuum.py. If not, see <http://www.gnu.org/licenses/>.


# This module depends on PySerial, a cross platform Python module
# to leverage the communication with the serial port.
# http://pyserial.sourceforge.net/pyserial.html#installation
# If you have `pip` installed on your computer, getting PySerial is as easy as
# pip install pyserial

import os
import threading
from datetime import datetime, timedelta
from time import sleep

import serial

OUT_DIR = "Z:/Experiments/SurfTOF/Measurements/rawData/pressure/"
LOG_FILE_EVERY = 15
LOG_HISTORY_EVERY = 2
HISTORY_HOURS = 168
GET_DATA_FROM_DEVICE_EVERY = 0.4


class MaxiGaugeLogger(threading.Thread):
    def __init__(self):
        super().__init__()
        self.mg = MaxiGauge(serial_port="COM3")
        self.last_date = datetime.now().date()
        self.output_file = open(f"{OUT_DIR}{self.last_date.strftime('%Y-%m-%d')}.txt", 'a')
        self.runner = 0
        self.values = []
        self.history = []
        try:
            self.labels = [v.strip() for v in self.mg.send('CID', 1)[0].split(',')]
        except Exception as e:
            print('class MaxiGaugeLogger',e)
            self.labels = [f"Sensor {i}" for i in range(1, 7)]

    def run(self):
        while True:
            self.runner += 1
            now = datetime.now()
            if now.date() > self.last_date:
                self.new_file(now.date())
            self.last_date = now.date()
            pressures = self.mg.pressures()
            err = 0
            for p in pressures:
                if p.status != 0:
                    err += 1
                    print("Error while reading:", p)
            if err < 6:
                self.values = [now] + [p.pressure for p in pressures]
                out_string = "\t".join(
                    [now.replace(microsecond=0).isoformat()] + [f"{p.pressure:.3e}" for p in pressures]
                )
                if self.runner % LOG_FILE_EVERY == 0:
                    self.output_file.write(f"{out_string}\n")
                if self.runner % LOG_HISTORY_EVERY == 0:
                    self.history.append(self.values)
                    while self.history[0][0] < now - timedelta(hours=HISTORY_HOURS):
                        self.history.pop(0)
                if self.runner % (LOG_FILE_EVERY * 5) == 0:
                    self.output_file.flush()
                    os.fsync(self.output_file.fileno())
            sleep(GET_DATA_FROM_DEVICE_EVERY)

    def new_file(self, date):
        self.close_file()
        self.output_file = open(f"{OUT_DIR}{date.strftime('%Y-%m-%d')}.txt", 'a')

    def close_file(self):
        try:  # close old file
            self.output_file.close()
        except:
            pass


class MaxiGauge(object):
    def __init__(self, serial_port, baud=9600, debug=False):
        self.debug = debug
        try:
            self.connection = serial.Serial(serial_port, baudrate=baud, timeout=0.2)
        except serial.serialutil.SerialException as se:
            raise MaxiGaugeError(se)

    def pressures(self):
        return [self.pressure(i + 1) for i in range(6)]

    def label(self):
        return self.send('TID')

    def pressure(self, sensor):
        if sensor < 1 or sensor > 6:
            raise MaxiGaugeError('Sensor can only be between 1 and 6. You choose ' + str(sensor))
        reading = self.send('PR%d' % sensor, 1)  # reading will have the form x,x.xxxEsx <CR><LF> (see p.88)
        try:
            r = reading[0].split(',')
            status = int(r[0])
            pressure = float(r[-1])
        except:
            raise MaxiGaugeError("Problem interpreting the returned line:\n%s" % reading)
        return PressureReading(sensor, status, pressure)

    def debug_message(self, message):
        if self.debug:
            print('debug_message', repr(message))

    def send(self, mnemonic, num_enquiries=0):
        self.connection.flushInput()
        self.write(mnemonic + LINE_TERMINATION)
        # if mnemonic != C['ETX']: self.read()
        # self.read()
        self.get_ACQ_or_NAK()
        response = []
        for i in range(num_enquiries):
            self.enquire()
            response.append(self.read())
        return response

    def write(self, what):
        self.debug_message(what)
        self.connection.write(what.encode())

    def enquire(self):
        self.write(C['ENQ'])

    def read(self):
        data = ""
        while True:
            x = self.connection.read().decode()
            self.debug_message(x)
            data += x
            if len(data) > 1 and data[-2:] == LINE_TERMINATION:
                break
        return data[:-len(LINE_TERMINATION)]

    def get_ACQ_or_NAK(self):
        return_code = self.connection.readline()
        self.debug_message(return_code)
        # The following is usually expected but our MaxiGauge controller sometimes forgets this parameter...
        # That seems to be a bug with the DCC command.
        # if len(return_code)<3: raise MaxiGaugeError('Only received a line termination from MaxiGauge.
        # Was expecting ACQ or NAK.')
        if len(return_code) < 3:
            self.debug_message('Only received a line termination from MaxiGauge. Was expecting ACQ or NAK.')
        if len(return_code) > 2 and return_code[-3] == C['NAK']:
            self.enquire()
            returned_error = self.read()
            error = str(returned_error).split(',', 1)
            print('get_ACQ_or_NAK', repr(error))
            errmsg = {'System Error': ERR_CODES[0][int(error[0])], 'Gauge Error': ERR_CODES[1][int(error[1])]}
            raise MaxiGaugeNAK(errmsg)
        if len(return_code) > 2 and return_code[-3] != C['ACQ']:
            self.debug_message('Expecting ACQ or NAK from MaxiGauge but neither were sent.')
        # if no exception raised so far, the interface is just fine:
        return return_code[:-(len(LINE_TERMINATION) + 1)]


class PressureReading(object):
    def __init__(self, gauge_id, status, pressure):
        if int(gauge_id) not in range(1, 7):
            raise MaxiGaugeError('Pressure Gauge ID must be between 1-6')
        self.id = int(gauge_id)
        if int(status) not in PRESSURE_READING_STATUS.keys():
            raise MaxiGaugeError('The Pressure Status must be in the range %s' % PRESSURE_READING_STATUS.keys())
        self.status = int(status)
        self.pressure = float(pressure)

    def status_msg(self):
        return PRESSURE_READING_STATUS[self.status]

    def __repr__(self):
        return "Gauge #%d: Status %d (%s), Pressure: %f mbar\n" % (
            self.id, self.status, self.status_msg(), self.pressure)


# ------ now we define the exceptions that could occur ------

class MaxiGaugeError(Exception):
    pass


class MaxiGaugeNAK(MaxiGaugeError):
    pass


# ------- Control Symbols as defined on p. 81 of the english
#        manual for the Pfeiffer Vacuum TPG256A  -----------
C = {
    'ETX': "\x03",  # End of Text (Ctrl-C)   Reset the interface
    'CR': "\x0D",  # Carriage Return        Go to the beginning of line
    'LF': "\x0A",  # Line Feed              Advance by one line
    'ENQ': "\x05",  # Enquiry                Request for data transmission
    'ACQ': "\x06",  # Acknowledge            Positive report signal
    'NAK': "\x15",  # Negative Acknowledge   Negative report signal
    'ESC': "\x1b",  # Escape
}

LINE_TERMINATION = C['CR'] + C['LF']  # CR, LF and CRLF are all possible (p.82)

# Mnemonics as defined on p. 85
M = [
    'BAU',  # Baud rate                           Baud rate                                    95
    'CAx',  # Calibration factor Sensor x         Calibration factor sensor x (1 ... 6)        92
    'CID',  # Measurement point names             Measurement point names                      88
    'DCB',  # Display control Bargraph            Bargraph                                     89
    'DCC',  # Display control Contrast            Display control contrast                     90
    'DCD',  # Display control Digits              Display digits                               88
    'DCS',  # Display control Screensave          Display control screensave                   90
    'DGS',  # Degas                               Degas                                        93
    'ERR',  # Error Status                        Error status                                 97
    'FIL',  # Filter time constant                Filter time constant                         92
    'FSR',  # Full scale range of linear sensors  Full scale range of linear sensors           93
    'LOC',  # Parameter setup lock                Parameter setup lock                         91
    'NAD',  # Node (device) address for RS485     Node (device) address for RS485              96
    'OFC',  # Offset correction                   Offset correction                            93
    'OFC',  # Offset correction                   Offset correction                            93
    'PNR',  # Program number                      Program number                               98
    'PRx',  # Status, Pressure sensor x (1 ... 6) Status, Pressure sensor x (1 ... 6)          88
    'PUC',  # Underrange Ctrl                     Underrange control                           91
    'RSX',  # Interface                           Interface                                    94
    'SAV',  # Save default                        Save default                                 94
    'SCx',  # Sensor control                      Sensor control                               87
    'SEN',  # Sensor on/off                       Sensor on/off                                86
    'SPx',  # Set Point Control Source for Relay xThreshold value setting, Allocation          90
    'SPS',  # Set Point Status A,B,C,D,E,F        Set point status                             91
    'TAI',  # Test program A/D Identify           Test A/D converter identification inputs    100
    'TAS',  # Test program A/D Sensor             Test A/D converter measurement value inputs 100
    'TDI',  # Display test                        Display test                                 98
    'TEE',  # EEPROM test                         EEPROM test                                 100
    'TEP',  # EPROM test                          EPROM test                                   99
    'TID',  # Sensor identification               Sensor identification                       101
    'TKB',  # Keyboard test                       Keyboard test                                99
    'TRA',  # RAM test                            RAM test                                     99
    'UNI',  # Unit of measurement (Display)       Unit of measurement (pressure)               89
    'WDT',  # Watchdog and System Error Control   Watchdog and system error control           101
]

# Error codes as defined on p. 97
ERR_CODES = [
    {
        0: 'No error',
        1: 'Watchdog has responded',
        2: 'Task fail error',
        4: 'IDCX idle error',
        8: 'Stack overflow error',
        16: 'EPROM error',
        32: 'RAM error',
        64: 'EEPROM error',
        128: 'Key error',
        4096: 'Syntax error',
        8192: 'Inadmissible parameter',
        16384: 'No hardware',
        32768: 'Fatal error'
    },
    {
        0: 'No error',
        1: 'Sensor 1: Measurement error',
        2: 'Sensor 2: Measurement error',
        4: 'Sensor 3: Measurement error',
        8: 'Sensor 4: Measurement error',
        16: 'Sensor 5: Measurement error',
        32: 'Sensor 6: Measurement error',
        512: 'Sensor 1: Identification error',
        1024: 'Sensor 2: Identification error',
        2048: 'Sensor 3: Identification error',
        4096: 'Sensor 4: Identification error',
        8192: 'Sensor 5: Identification error',
        16384: 'Sensor 6: Identification error',
    }
]

# pressure status as defined on p.88
PRESSURE_READING_STATUS = {
    0: 'Measurement data okay',
    1: 'Underrange',
    2: 'Overrange',
    3: 'Sensor error',
    4: 'Sensor off',
    5: 'No sensor',
    6: 'Identification error'
}
