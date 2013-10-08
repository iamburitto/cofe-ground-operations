from telnetlib import Telnet
import math
import time

class Galil(object):
    def __init__(self, ip, port, poll=False, queue=None):
        """A class which facilitates interaction with the galil controller"""

        self.con = Telnet(ip, port)
        self.positions = [0, 0]

    def send_read(self, cmd):
        """Sends a galil command to the controller, then returns the result"""

        #First, we need to clear the input buffer, because we want to get rid of any previous strings
        try:
            self.con.read_very_eager()
        except:
            pass
        self.con.write( cmd+';')           # send the command string
        time.sleep(0.030)               # give some time for the galil to respond

        #get the response and strip off the garbage the galil sends to make interacting with it over telnet easier.
        return self.con.read_very_eager().rstrip(":").strip()

    def __optional(self, x_i):
        """Logic for commands with optional arguments."""
        return '' if x_i is None else chr(65+x_i)

    def __command(self, command, *args):
        """Sends commands and returns their results."""
        if len(args)==1: #all commands with optional axis specifiers
            args = map(self.__optional, args) #accept only one argument
        else: #all commands with two args start by specifiing the axis
            args = chr(65+args[0]), args[1] #which must be turned into a letter
        #print command.format(*args)
        return self.send_read(command.format(*args))

    def move_to(self, x_i, p):
        """Moves to the position p on axis x_i."""
        #print p
        #print self.__command("PA{}={}", x_i, p)
        #print self.begin_motion(x_i)
        return self.__command("PA{}={}", x_i, p)

    def move_steps(self, x_i, dp):
        """Moves the position dp steps on the axis x_i."""
        #print dp
        #print self.__command("PR{}={}", x_i, dp)
        #print self.begin_motion(x_i)
        return self.__command("PR{}={}", x_i, dp)

    def set_slewspeed(self, x_i, v):
        """Sets the slew speed of axis x_i to v."""
        return self.__command("SP{}={}", x_i, v)

    def set_jogspeed(self, x_i, v):
        """Sets the jogspeed of axis x_i to v."""
        return self.__command("JG{}={}", x_i, v)

    def get_position(self, x_i=None):
        """Returns the position of axis x_i.
        If x_i is None, returns a every position.
        The returned value is either an int or a tuple of ints."""
        x = self.__command("TP{}", x_i)
        #print x
        return eval(x)
    
    def begin_motion(self, x_i=None):
        """Begins motion on axis x_i.
        If x_i is None, motion begins on all axes."""
        return self.__command("BG{}", x_i)

    def in_motion(self, x_i):
        """Checks if axis x_i is in motion. returns a bool."""
        return bool(eval(self.__command("MG _BG{}", x_i)))

    def end_motion(self, x_i=None):
        """Stops motion on axis x_i.
        If x_i is None then motion is stopped on all axes."""
        return self.__command("ST{}", x_i)

    def motor_on(self, x_i=None):
        """Turns on the axis x_i.
        If x_i is None then all axes are turned on."""
        return self.__command("SH{}", x_i)

    def is_motor_on(self, x_i=0):
        """Returns True if axis x_i is on, else False."""
        return "0.0000" == self.__command("MG _MO{}", x_i)


    def motor_off(self, x_i=None):
        """Turns off the axis x_i.
        If x_i is None, then all axes are turned off."""
        return self.__command("MO{}", x_i)

    def scan(self, x_i, degrees, period, cycles):
        # max_accel = max_deccel = 1e6
        #initial_angle = 0
        self.motor_on(x_i) #make sure a motor is on
        frequency = 1.0/period
        #convert degrees to an amplitude in encoder counts
        frequency = 1.0/period
        radius = int(degrees/9.*12800)
        axis_letter = chr(65+x_i)
        code = "VM{0}N;VA {1};VD {1};VS {2};CR {3}, 0, {4};VE;BGS"
        code = code.format(axis_letter,
                           1e6, #max accel and deccel
                           int(2*math.pi*radius*frequency),
                           radius,
                           360*cycles)
        for line in code.split(';'):
            print line
            self.con.write(line+';')
            time.sleep(0.03)

    def close(self, motors_off=True):                  #Optionally turn the motors off, and then try to close the socket
                                        # connection gracefully
        if self.con:
            try:                            # Since this is called by both the GUI and the destructor, we have to simply catsh and ignore errors here.
                print "Closing Connection"     # otherwise, there are errors arising from the fact that it winds up trying to close a closed connection.
                if motors_off: self.motor_off()
                self.con.close()
                self.con = None
            except:
                pass
    def __del__(self):
        self.close()
