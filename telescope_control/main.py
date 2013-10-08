from gui import MyFrame
from galil import Galil
from config import Config
from units import Units
import time, wx

class MainWindow(MyFrame):
    def __init__(self, galil, converter, *args, **kwargs):
        MyFrame.__init__(self, *args, **kwargs)
        self.poll_update = wx.Timer(self)
        self.galil = galil
        self.converter = converter

        #wx.EVT_TIMER(self, self.poll_update.GetId(), self.update_display)
        self.Bind(wx.EVT_TIMER, self.update_display, self.poll_update)
        self.poll_update.Start(50)


    def stop(self, event):
        stops = [(self.button_stop_all, None),
                 (self.button_stop_az, 0),
                 (self.button_stop_el, 1)]
        for stop, axis in stops:
            if event.GetId() == stop.GetId():
                self.galil.end_motion(axis)
                break
        event.Skip()

    def toggle_motor_state(self, event):
        axis = 0
        if event.GetId() == self.button_el_motor.GetId():
            axis = 1
        if self.galil.is_motor_on(axis):
            self.galil.motor_off(axis)
        else:
            self.galil.motor_on(axis)
        event.Skip()

    def set_step_size(self, event):
        degrees = int(self.step_size_input.GetValue())
        self.step_size = [self.converter.az_to_encoder(degrees),
                          self.converter.el_to_encoder(degrees)]
        event.Skip()

    def move_rel(self, event):
        b_c_a = [(self.button_up, 1, 1),
                   (self.button_down, -1, 1),
                   (self.button_right, 1, 0),
                   (self.button_left, -1, 0)]
        for button, c, axis in b_c_a:
            if event.GetId()==button.GetId():
                try:
                    self.galil.move_steps(axis, c*self.step_size[axis])
                except AttributeError:
                    print "Can't move! No step size entered!"
                    print "To enter a step size, type a number of degrees in"
                    print "the box near the arrows, and press enter."
                except:
                    print "WUT"
                else:
                    self.galil.begin_motion(axis)
                break
        event.Skip()
        return

    def scan(self, event):
        scan_type = self.scan_options.GetValue()
        if scan_type == "Azimuth":
            vals = [self.scan_period_input.GetValue(),
                    self.scan_cycles_input.GetValue(),
                    self.scan_min_az_input.GetValue(),
                    self.scan_max_az_input.GetValue()]
            vals = map(int, vals)
            period, cycles = vals[:2]
            degrees = vals[3]-vals[2]
            self.galil.scan(0, degrees, period, cycles)
        else:
            print "{} scan not implemented!".format(scan_type)
        event.Skip()

    def update_display(self, event):
        #print "updating"
        statuses = [(self.az_status, "Az: "),
                    (self.el_status, "El: "),
                    (self.ra_status, "Ra: "),
                    (self.dec_status,"Dec: "),
                    (self.local_status, "Local: "),
                    (self.lst_status, "Lst: "),
                    (self.utc_status, "Utc: ")]
        while True: #Sometimes the galil responds with 
            try:    #an empty string. When it does
                data = list(self.galil.get_position())
            except: #try again.
                continue
            else: #Otherwise, break the loop.
                break
        data = [self.converter.encoder_to_az(data[0]),
                self.converter.encoder_to_el(data[1])]
        data += list(self.converter.azel_to_radec(*data))
        data += [self.converter.lct(),
                 self.converter.lst(), 
                 self.converter.utc()]
        data = map(str, data)
        map(lambda (widget, prefix))
        for (widget, prefix), datum in zip(statuses, data):
            widget.SetLabel(prefix + datum)
        event.Skip()
        return

if __name__ == "__main__":
    config = Config("config.txt")
    galil = Galil(config["IP"], config["PORT"])
    converter = Units(config)
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MainWindow(galil, converter, None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
