import socket as client


class Ema:

    def __init__(self, ip, port, prompt="Enter command:"):
        self.ip_port = (ip, port)
        self.prompt = prompt.strip()
        self.ema = client.socket(client.AF_INET, client.SOCK_STREAM)

    def connect(self):
        self.ema.connect(self.ip_port)
        final_response = ''
        user_connected = False
        while True:
            data = self.ema.recv(2048) # 2K
            res = data.decode('utf-8')
            final_response += res
            if final_response.find(self.prompt) != -1:
                user_connected = True
                break
        return user_connected

    def send_command(self, cmd):
        if cmd[-1] != ';':
            cmd += ';'
        cmd += "\r\n"
        self.ema.send(bytes(cmd.encode()))
        final_response = ''
        while True:
            data = self.ema.recv(1024)
            res = data.decode()
            partial_res =  res.strip().strip(self.prompt).strip()
            final_response += partial_res
            if len(partial_res) > 0 and partial_res[-1] == ";":
                break
        return final_response

    def logout(self):
        self.ema.send(b'LOGOUT;')

    def login(self, user, password):
        cmd = f"LOGIN:{user}:{password};"
        reply = self.send_command(cmd)
        return reply.startswith("RESP:0")

    def get_user_info(self, subno):
        cmd = f"GET:HLRSUB:MSISDN,245{subno};"
        reply = self.send_command(cmd)
        return reply

    def create_subscriber(self, subno, imsi, profile):
        return self.send_command(f"CREATE:HLRSUB:MSISDN,245{subno}:IMSI,{imsi}:PROFILE,{profile};")
    
    def delete_subscriber(self, subno):
        return self.send_command(f"DELETE:HLRSUB:MSISDN,245{subno};")

    def remove_all_barring(self, subno):
        ret = {}
        obo = f"SET:HLRSUB:MSISDN,245{subno}:OBO,0;" # Outgoing calls
        obi = f"SET:HLRSUB:MSISDN,245{subno}:OBI,0;" # Incoming calls
        baoc = f"SET:HLRSUB:MSISDN,245{subno}:BAOC,0;" # All Outgoing calls
        baic = f"SET:HLRSUB:MSISDN,245{subno}:BAIC,0;" # All incoming calls
        boic = f"SET:HLRSUB:MSISDN,245{subno}:BOIC,0;" # All Outgoing International
        cfnrc = f"SET:HLRSUB:MSISDN,245{subno}:CFNRC,0;"
        ret['obo'] = self.send_command(obo).strip()
        ret['obi'] = self.send_command(obi).strip()
        ret['baoc'] = self.send_command(baoc).strip()
        ret['baic'] = self.send_command(baic).strip()
        ret['boic'] = self.send_command(boic).strip()
        ret['cfnrc'] = self.send_command(cfnrc).strip()
        return ret

    def close(self):
        self.logout()
        self.ema.close()
        print("Logged out")


if __name__ == "__main__":
    ema = Ema("10.195.5.7", 3300)
    ema.connect()
    is_cononected = ema.login("emamtngb", "EmaMtnBiss@u19")
    numbers = ['966601471', '966601924','966601571','966601590','966601771', '966601923', '966002971', '966002972', '455244dfdf', '966601471', '966601924','966601571','966601590','966601771', '966601923', '966002971', '966002972', '455244dfdf']
    # numbers = ['965322564']
    if is_cononected:
        for subno in numbers:
            print(ema.get_user_info(subno))
            # print(ema.remove_all_barring(subno))
        # print(ema.delete_subscriber('966655661'))
        # print(ema.create_subscriber('966655661', '632020105570318', 111))
    else:
        print("Not connected.")
    
    # print(server.remove_all_barring('966655661'))
    ema.close()
