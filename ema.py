import socket as client


class Ema:

    def __init__(self, ip, port, prompt="Enter command: "):
        self.ip_port = (ip, port)
        self.prompt = prompt
        self.ema = client.socket(client.AF_INET, client.SOCK_STREAM)

    def connect(self):
        self.ema.connect(self.ip_port)

        final_response = ''
        user_connected = False
        while True:
            data = self.ema.recv(1024*2)
            res = data.decode('utf-8')
            final_response += res
            # print('Final: ' + final_response)
            if final_response.find(self.prompt) != -1:
                user_connected = True
                break
        return user_connected

    def send_command(self, cmd):
        self.ema.send(bytes(cmd.encode()))
        final_response = ''
        while True:
            #print('before receive')
            data = self.ema.recv(1024)
            #print('after receive')
            res = data.decode('utf-8')
            final_response += res
            #print('before if')
            if res[-1] == '\n' or res[-1] == ';':
                break
        index = final_response.find(self.prompt)
        if index != -1:
            return final_response[index+len(self.prompt):]
        return final_response

    def logout(self):
        self.ema.send(b'LOGOUT;')

    def login(self, user, password):
        cmd = f"LOGIN:{user}:{password};\n"
        reply = self.send_command(cmd)
        # print('LOGIN reply ' + reply)
        t = reply.split(':')[1][0]
        return t == '0'

    def get_info(self, subno):
        cmd = f"GET:HLRSUB:MSISDN,245{subno};\n"
        reply = self.send_command(cmd)
        return reply

    def close(self):
        self.logout()
        self.ema.close()


if __name__ == "__main__":
    server = Ema("10.195.5.7", 3300)
    server.connect()
    is_cononected = server.login("emamtngb", "EmaMtnBiss@u19")
    numbers = ['966601471', '966601924','966601571','966601590','966601771']
    if is_cononected:
        for subno in numbers:
            print(server.get_info(subno))
    else:
        print("Not connected.")
    server.close()
