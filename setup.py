import serial
import serial.tools.list_ports
import difflib


def MKS_PDR900(port_address):
    inst = serial.Serial(port_address, timeout=1)
    return inst


def find_port():
    """

    :return: the port of the controller
    """
    ports = serial.tools.list_ports.comports()
    available_ports = []
    for p in ports:
        available_ports.append(p.device)
    port = difflib.get_close_matches('/dev/cu.usbserial-', available_ports)
    if not port:
        print('No port found for transducer controller.')
        quit()
    else:
        print('Transducer controller port (' + port[0] + ') found.')
    return port[0]


# For more command and query syntax, please refer to the manual
# (https://www.lesker.com/newweb/gauges/pdf/kjlc-mks-pdr900-vacuum-gauge-controller-manual.pdf), page 15.
cmd_syntax = {
    'baud rate': '@001BRC?;FF',
    'serial number': '@001SNC?;FF',
    'download': '@001DL?;FF',
    'datalogger timer': '@001DLT?;FF',
    'datalogger start': '@001DLC!START;FF',
    'datalogger stop': '@001DLC!STOP;FF'
}
