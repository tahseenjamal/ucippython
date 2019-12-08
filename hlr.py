import time
import telnetlib

class Hlr:

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.telnet = None
    
    def connect(self):
        self.telnet = telnetlib.Telnet(self.host, port=5000, timeout=20)
        self.telnet.read_until(b'USERCODE: ')
        self.telnet.write('ITadmin'.encode() + b"\r\n")
        self.telnet.read_until(b'PASSWORD: ')
        self.telnet.write('MtnBissau1'.encode() + b"\r\n")
        self.telnet.read_until(b'DOMAIN: ')
        self.telnet.write(b"\r\n")
        self.telnet.read_until(b'<')
    
    def send_command(self, cmd):
        if self.telnet == None:
            raise Exception('Exception: You are not connected to HLR. Please call connect() method before send command')
        if cmd[-1] != ';':
            cmd += ';'
        self.telnet.write(cmd.encode() + b"\r\n")
        response = self.telnet.read_until(b'<').decode()
        return response


    def close(self):
        rr = self.send_command("EXIT;")
        self.telnet.close()


if __name__ == '__main__':
    h = Hlr('10.180.8.18', 'ITadmin', 'MtnBissau1')
    h.connect()
    r = h.send_command("hgsdp:msisdn=245966601471,all")
    print(r)
    h.close()

