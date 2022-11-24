import bluetooth
import os 
from Autotest import DUT

class Socketserver(object):
    """docstring for Socketserver"""
    def __init__(self, macaddress):
       self.macaddress=macaddress

    def run(self):

        os.system("hciconfig hci0 up")
        os.system("hciconfig hci0 piscan")

        #apt-get install libbluetooth-dev


        server_sock=BluetoothSocket(RFCOMM)
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee" # Uuid inventato, dobbiamo discutere su come generarlo per tuttu

        advertise_service( server_sock, "MoviBleSocket",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ], 
        #                   protocols = [ OBEX_UUID ] --> E' un protocollo per il trasferimento binario. Non ci serve ma ricordiamoci che esiste
                         )
     
        client_sock , client_info = server_sock.accept()

        while client_info != macaddress:


        try:
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0: break
                print("received [%s]" % data)
                # data sarà la richiesta di dati dell'app, a cui bisogna rispondere
                if data == b'getNewData':
                    client_sock.send("000102030405060708090A0B0C0D0E0F")
        except IOError:
            pass

        client_sock.close()
        server_sock.close()


class Socketclient(object):
    """docstring for Socketclient"""
    def __init__(self, macaddress):
        self.addr=macaddress

    def run(self):

        #turn on the BLE interface
        os.system("hciconfig hci0 up")
        os.system("hciconfig hci0 piscan")

        # search for the SampleServer service
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        service_matches = bluetooth.find_service(uuid=uuid, address=self.addr)

        while len(service_matches) == 0:
            print("Couldn't find the SampleServer service.")
            service_matches = bluetooth.find_service(uuid=uuid, address=self.addr)

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        print("Connecting to \"{}\" on {}".format(name, host))

        # Create the client socket
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((host, port))

        poisonPill = False

        while not poisonPill:
            
            data_rcv = string(sock.recv(1024))
            print(data_rcv)

            if data_rcv == b'kill':
                poisonPill = True

            elif data_rcv == b'autotest':
                dut = DUT()
                inMask = dut.getInStatus()
                outMask = dut.getOutStatus()

                sock.send("in:{},out:{}".format(inMask, outMask))

        #close the socket
        sock.close()

        #turn off the BLE interface
        os.system("hciconfig hci0 down")



   
            
                
