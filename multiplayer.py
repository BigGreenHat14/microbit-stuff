# Imports go at the top
import radio
from microbit import sleep, running_time
class PlayerLimitError(Exception):
    """Exception raised when the player limit is reached."""
    pass

class Multiplayer:
    """
    Multiplayer class for handling radio-based multiplayer interactions
    on the micro:bit platform.
    """
    def receive_command(self):
        c = radio.receive()
        if c:
            return c.split("=")
    def send_command(self,*cmd,p=""):
        radio.send(str(p) + ("-" if p else "") + ("=".join([str(i) for i in cmd])))
    def __init__(self, group_id=0, player_limit=0):
        """
        Initializes the multiplayer session.
        
        :param group_id: Radio group id.
        :param player_limit: Maximum allowed number of players (0 means unlimited).
        :raises PlayerLimitError: If joining fails because the player limit is reached.
        """
        self.player_limit = player_limit
        self.requests = []
        self._return = None
        self.request_names = []
        self._returnid = 0
        self.player_number = 1
        self.msgcache = []
        self.total_players = 1
        radio.on()
        radio.config(channel=42, group=group_id)
        
        for _ in range(4):
            radio.send("j")
            sleep(100)
            received = self.receive_command()
            if received:
                if received[0] == "p":
                    if received[1] == "0":
                        raise PlayerLimitError("Failed to join, Player limit reached")
                    self.player_number = int(received[1])
                    self.total_players = int(received[1])
                    break
    def request(self,name):
        self.request_names.append(name)
        def dec(callback):
            self.requests.append(callback)
            return callback
        return dec
    def receive_message(self):
        if self.msgcache:
            toreturn = self.msgcache[0:1]
            del self.msgcache[0]
            return toreturn
    def send_message(self,player,message):
        self.send_command("c",message,p=player)
    def main_loop(self):
        cmd = self.receive_command()
        if cmd:
            op = cmd[1:]
            cmd = cmd[0]
            if cmd == "j" and self.player_number == 1:
                if self.total_players == self.player_limit:
                    self.send_command("p",0)
                self.total_players += 1
                self.send_command("p",self.total_players)
            elif cmd == "p":
                if op[0] != "0":
                    self.total_players = int(op[0])
            elif cmd.startswith(str(self.player_number)):
                a = cmd.split("-")
                if a:
                    if a[0] == str(self.player_number):
                        cmd = cmd.split("-")
                        if cmd[1] == "r":
                            self._return = op
                        elif cmd[1] == "m":
                            self.msgcache.append("=".join(op))
                        else:
                            self.send_command("r",str(self.requests[int(cmd[1])](*op[1:])),p=op[0])
    def send_request(self,to,name,*params,timeout=2.0):
        timeoutms = round(timeout * 1000)
        start = running_time()
        params = [str(i) for i in params]
        if to == self.player_number:
            return str(self.requests[self.request_names.index(name)](*params))
        self._return = None
        self.send_command(self.request_names.index(name),self.player_number,*params,p=to)
        while self._return == None and not running_time() - start > timeoutms:
            self.main_loop()
        if running_time() - start > timeout:
            return None
        return "=".join(self._return)#type:ignore

if __name__ == "__main__":
    from microbit import display, Image, button_a, button_b
    display.show(Image('99900:00090:99009:00909:90909'))
    try:
        mp = Multiplayer(player_limit=2)
    except PlayerLimitError:
        display.show(Image.NO)
        raise KeyboardInterrupt
    display.show(mp.player_number)
    sleep(300)
    display.clear()

    @mp.request("down")
    def down(button):
        if button == "b":
            display.show(Image.SAD)
        else:
            display.show(Image.HAPPY)
    @mp.request("up")
    def up():
        display.clear()

    while True:
        mp.main_loop()
        if button_a.is_pressed():
            mp.send_request(2,"down","a",timeout=0.1)
            while button_a.is_pressed(): mp.main_loop()
            mp.send_request(2,"up",timeout=100)
        elif button_b.is_pressed():
            mp.send_request(2,"down","b",timeout=0.1)
            while button_b.is_pressed(): mp.main_loop()
            mp.send_request(2,"up",timeout=0.1)
    