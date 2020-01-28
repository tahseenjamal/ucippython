import time
import telnetlib

class Hlr:

    def __init__(self, host, username, password):
        self.host = host
        self.username = username + "\r\n"
        self.password = password + "\r\n"
        self.telnet = None
    
    def connect(self):
        self.telnet = telnetlib.Telnet(self.host, port=5000, timeout=20)
        self.telnet.read_until(b'USERCODE: ')
        self.telnet.write(self.username.encode())
        self.telnet.read_until(b'PASSWORD: ')
        self.telnet.write(self.password.encode())
        self.telnet.read_until(b'DOMAIN: ')
        self.telnet.write(b"\r\n")
        self.telnet.read_until(b'<')
    
    def send_command(self, cmd):
        if self.telnet == None:
            raise Exception('Exception: You are not connected to HLR. Please call connect() method before send command')
        if cmd[-1] != ';':
            cmd += ';'
        cmd += "\r\n"
        self.telnet.write(cmd.encode())
        response = self.telnet.read_until(b'<').decode()
        return response

    def get_user_info(self, subno):
        return self.send_command(f"hgsdp:msisdn=245{subno},all")
    

    def create_user(self, subno, imsi, profile):
        #111 ==> prepaid, 200 ==> postpaid
        return self.send_command(f"HGSUI:MSISDN=245{subno},IMSI={imsi},PROFILE={profile}")

    def set_subscriber_imsi(self, subno, imsi):
        return self.send_command(f"HGICI:MSISDN=245{subno},NIMSI={imsi}")

    def close(self):
        self.send_command("EXIT;")
        self.telnet.close()


if __name__ == '__main__':
    h = Hlr('10.180.8.18', 'ITadmin', 'MtnBissau1')
    h.connect()
    r = h.get_user_info("966601471")
    print(r)
    h.close()

