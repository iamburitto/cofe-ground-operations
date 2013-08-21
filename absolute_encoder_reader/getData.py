from PyDAQmx import *
from PyDAQmx.DAQmxCallBack import *
from numpy import zeros
""" 
functions to get DIO data and parse in to Az encoder, El encoder and 24 bit counter numbers
Mappings to DIO board  P

****** Elevation Encoder (J4) ******
P10.7 - P10.2 = J4.1  - J4.6    (MSB=J4.1, LSB=J4.18)
P7.7  -  P7.2 = J4.7  - J4.12
P4.7  -  P4.2 = J4.13 - J4 .18
****** Azimuth Encoder (J2) ******
P5.0  -  P5.7 = J2.16 - J2.9    (MSB=J2.1, LSB=J2.16)
P2.0  -  P2.7 = J2.8  - J2.1
****** 24 bit counter (J5) ******
P0.7  -  P0.0 = J5.23 - J5.16   (MSB=J4.1, LSB=J4.18)
P3.7  -  P3.0 = J5.15 - J5.8
P9.7  -  P9.0 = J5.7  - J5.0
"""
class Eyeball(object):
	def __init__(self):
		self.data = numpy.zeros((97,), dtype=numpy.uint8)
		self.i = 0
		self.err=""
		self.read, self.bytesPerSamp=int32(), int32()
		DAQmxResetDevice('dev1')
		self.taskHandle=TaskHandle()
		
		DAQmxCreateTask("",byref(self.taskHandle))
		

		DAQmxCreateDIChan(self.taskHandle,"Dev1/port10","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port7","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port4","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port2","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port5","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port0","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port3","",DAQmx_Val_ChanForAllLines)
		DAQmxCreateDIChan(self.taskHandle,"Dev1/port9","",DAQmx_Val_ChanForAllLines)
		
		DAQmxStartTask(self.taskHandle)

	def close(self):
		print "bye"
		
		DAQmxStopTask(self.taskHandle)
		DAQmxClearTask(self.taskHandle)

	def __del__(self):
		#self.close()
		pass

	def getData(self):
		
		DAQmxReadDigitalLines(self.taskHandle,1,10.0,DAQmx_Val_GroupByChannel,self.data,100,byref(self.read),byref(self.bytesPerSamp),None)
		index=0
		all = [self.data[d] for d in range(0,95)]
		all = map(str, all) 

		return  [''.join((all[2:8])[::-1])+''.join((all[10:16])[::-1])+''.join((all[18:24])[::-1]), ''.join((all[24:32])[::-1])+"".join((all[32:40])[::-1]), ''.join((all[40:48])[::-1])+''.join((all[48:56])[::-1])+''.join((all[56:64])[::-1])]

	
if __name__=='__main__':
	t = Eyeball()
	#t.getData()
	print t.getData()



		

		
		
		
