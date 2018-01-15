from time import sleep
import telnetlib
from socket import gaierror, timeout
class ThermotronChamber():
	"""
	Class to connect to a 8800 controller on a Thermotron chamber
	"""
	def __init__(self, chamber_control_name, description = None, portNumber="8888", simulate=False):
		self.chamber_control_name = chamber_control_name
		self.portNumber = portNumber
		self.description = description
		self.simulate = simulate
		# Try and connect to the thermal chamber:
		if self.simulate:
			print("Simulating chamber for {}...".format(chamber_control_name))
			self.simul_temperature = 25
			self.simul_temp_temp = 0
			self.simul_ramp = 3
			self.simul_temp_ramp = 0
		else:
			print("Trying to connect to {}...".format(chamber_control_name))
			try:
				self.tn = telnetlib.Telnet(host = chamber_control_name,
	                port = portNumber,
	                timeout = 1)
				print("Successfully opened a terminal to {}".format(chamber_control_name))
			except gaierror as e:
				# print("\n".join(dir(e)))
				print(e.strerror)
				print("Could not locate that chamber name. Check network connection and/or thermal chamber name")
				exit(1)
			except timeout as e:
				print("Failed to open a terminal to {}, connection timed out".format(chamber_control_name))
				exit(1)
			except ConnectionRefusedError as e:
				print(e.strerror)
				exit(1)

	def __unicode__(self):
		if self.description:
			return '{0}:{1}'.format(self.chamber_control_name,
				self.description)
		return self.chamber_control_name

	def __str__(self):
		return self.__unicode__()

	def __del__(self):
		try:
			print("Closing the terminal for {}.".format(self.chamber_control_name))
			self.tn.close()
		# In case we haven't initiated a console to the chamber yet.
		except AttributeError as e:
			pass

	def __repr__(self):
		return "<thermotron_ctrl {}>".format(self.__unicode__())

	def get_alarm_status(self, port):
		"""
		The 8800 returns the current alarm status for the selected channel
		(0 = Low deviation alarm, 1 = High deviation alarm)
		"""
		if self.simulate:
			return 0
		if int(port) in range(1,9):
			command_string = "ALRM{}?\r".format(port)		
		else:
			print("Port number out of range.")
			return 0

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()


	def get_set_aux(self, aux_group, status_int=None):
		"""
		The query command allows you to read the on and off states of the auxiliary groups (1 or 2),
		Auxiliary group 1 refers to auxiliaries 1-8 and Auxiliary Group 2 refers to auxiliaries 9-16.
		The operation command allows you to change the auxiliary states for run manual mode
		operations and/or edit from hold operations.
		"""
		if self.simulate:
			return 0
		if isinstance(status_int,float) or isinstance(status_int,int):
			command_string = "AUXE{0},{1}\r".format(aux_group,status_int)
		else:
			command_string = "AUXE{0}\r".format(aux_group)
		
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_channel_config_information(self, pvchannel):
		"""
		The 8800 sends a single coded integer describing the channel type.
		0 = Channel not used
		1 = Percent relative humidity channel using a wet bulb/dry bulb thermocouple pair
		2 = Temperature channel using a thermocouple
		3 = Linear channel using a programmable range (for example altitude)
		4 = Linear 0% to 100% relative humidity channel using a solid-state sensor
		5 = Product temperature control channel
		"""
		if self.simulate:
			return 0
		if pvchannel in range(1,9):
			command_string = "CCNF{}?\r".format(pvchannel)
		else:
			return None

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_channel_on_and_configured_status(self):
		"""
		The 8800 sends a two-byte coded integer describing the channel on and configuration status.
		Byte 1 = channel on status: Bits 0 through 7 indicate the configured status of channels 1-8
		respectively. The 8800 sets the bit for each channel that is on.

		Byte 2 = channel configured status: Bits 8 through 15 indicate the configured status of
		channels 1-8 respectively. The 8800 sets the bit for each channel that is configured.
		"""
		if self.simulate:
			return 0
		command_string = "CHST?\r"
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_channel_name(self, channel):
		"""
		This command allows you to tread the assigned name of any process variable or monitor channel.
		"""
		if self.simulate:
			return 0
		if channel in range(1,29):
			command_string = "CNAM{}?\r".format(channel)
		else:
			return None

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()		

	def get_set_deviation(self, channel, deviation=None):
		"""
		Asks the 8800 for the current deviation reading from a selected channel.
		The 8800 sends the value in the channel's selected units. the operation command loads a
		deviation setting into the 8800 for the current manual mode operation, or sends a temporary
		deviation value during an edit from hold operation.
		"""
		if self.simulate:
			return 0
		command_string = ""
		if int(channel) in range(1,5) and (isinstance(deviation,float) or isinstance(deviation,int)):
			command_string = "DEVN{0},{1}\r".format(channel,deviation)
		elif int(channel) in range(1,5):
			command_string = "DEVN{0}?\r".format(channel)

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def set_hold(self):
		"""
		Places a running program or test in hold mode
		"""
		if self.simulate:
			return 0
		command_string = "HOLD\r"
		self.tn.write(command_string.encode("ascii"))
		return self.tn.read_some().decode("ascii").strip()

	def get_iden(self):
		"""
		Send device identification
		"""
		if self.simulate:
			return 0
		command_string = "IDEN?\r"
		self.tn.write(command_string.encode("ascii"))
		return self.tn.read_some().decode("ascii").strip()

	def get_set_light(self, status=-1, Toggle = False):
		"""
		Asks the 8800 for the status of the light.
		The operation comand allows you to remotely turn the chamber light on or off.
		If toggle is true, queries the 8800 and toggles the light regardless
		of what status is.
		"""
		if self.simulate:
			return 0
		if Toggle:
			command_string = "LGHT?\r".format(int(status))
			self.tn.write(command_string.encode("ascii"))
			status = 1-int(self.tn.read_some().decode("ascii").strip())

		if int(status) in [0, 1]:
			command_string = "LGHT{}\r".format(int(status))
		else:
			command_string = "LGHT?\r".format(int(status))

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()
	
	def get_set_manual_ramp(self, channel, ramp=None):
		"""
		Manual mode command. The query command reads the manual ramp setting for the 
		selected channel in units per minute. The units are in the scale selected at the 8800
		(such as C, F, torr, %\RH, etc.)
		"""
		if self.simulate and ramp:
			self.simul_temp_ramp = ramp
			return 0
		elif self.simulate:
			return self.simul_ramp

		command_string = ""
		if channel in range(1,5) and (isinstance(ramp,int) or isinstance(ramp, float)):
			command_string = "MRMP{},{}\r".format(channel,ramp)
		elif channel in range(1,5):
			command_string = "MRMP{}?\r".format(channel)


		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_set_options(self, option_int=-1):
		"""
		Reads the options register of the 8800. If the 8800 is in manual mode, the
		operation command temporarily changes the 8800 options to the new set of options.
		Note: If the selected options are not on your chamber, the 8800 will return an
		error code.

		1=Product temperature control
		2=Humidity System
		4=Low humidity system
		8=GSoak
		16=Purge
		32=Cascade refrigeration (SE-Series chambers only)
		64=Power save mode (SE-Series chambers only)
		128=Single-stage refrigeration (SE-Series Only)
		256=Rapid cycle operation(AST modules only)
		512=Rapid cycle operation(AST modules only)

		The code provides a value between 0 and 1023 that is the sym of the values of all the
		enables options. For example, a 49 indicates that the cascade refrigeration system, purge,
		and product temperature control options are enabled.
		"""
		if self.simulate:
			return 0

		if int(option_int) in range(0,1024):
			command_string = "OPTN{}\r".format(str(option_int).zfill(3))
		else:
			command_string = "OPTN?\r"

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_set_parameter_group(self, parameter_group=None):
		"""
		Queries the 8800 for the number of the parameter group that it is currently using. if the 8800
		is in manual mode, the operation command selects the parameters group (1 to 4) that the 8800
		will use to control the channels. Edit from hold operations temporarily change the parameter
		group for the program.
		"""
		if self.simulate:
			return 0

		if parameter_group in range(1,5):
			command_string = "PRMG,{}\r".format(parameter_group)
		else:
			command_string = "PRMG?\r"

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_process_variable(self, pvchannel=None):
		"""
		Queries the 8800 for the current value of the selected channel. The channel selections for the
		PVAR command are defined as follows:
		1-4: External process variable channels 1 through 4
		5-8: Internal process variable channels 5 through 8
		9-12: Undefined
		13-28: Monitor channels 1 through 16
		29-32: Undefined
		33-36: System Monitor temperature channels for refrigeration system 1
		37-48: System Monitor channels for refrigeration systems 2,3, and 4
		"""
		if self.simulate:
			return self.simul_temperature

		if pvchannel in range(1,49):
			command_string = "PVAR{}?\r".format(pvchannel)
		else:
			return

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()


	def set_manual_run(self):
		"""
		Places a stopped 8800 in run manual mode.
		"""
		if self.simulate:
			self.simul_temperature = self.simul_temp_temp
			self.simul_ramp = self.simul_temp_ramp
			return 0

		command_string = "RUNM\r"
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_stop_status(self):
		"""
		The stop code identifies the cause of the most recent transition to the stop state.
		The stop codes are defined as follows:

		0 Cold boot power up. The 8800 memory has been initialized.
		1 Currently running. not in stop
		2 Stop key pressed.
		3 End of test.
		4 External input. An input defined as stop has been activated.
		5 Computer interface. The 8800 received the stop command.
		6 Open input. A thermocouple or analog input is open.
		7 Process alarm. A process alarm setting has been exceeded.
		8 System Monitor trip.
		9 Power fail recovery. The selected power fail recover mode was stop.
		10 Therm-Alarm trip.
		"""
		if self.simulate:
			return 1

		command_string = "SCOD?\r"
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_set_setpoint(self, channel, setpoint=None):
		"""
		The query command asks the 8800 for the current set point reading from channel. there
		8800 sends the set point value in the channel's selected units. In manual mode, the
		operation command loads a new set point into the 8800 for the current operation.
		1=Air Temp
		2=Humidity
		3=PTC
		"""
		if self.simulate and setpoint:
			self.simul_temp_temp = setpoint
			return 0
		elif self.simulate:
			return self.simul_temperature

		command_string = ""
		if channel in range(1,5) and (isinstance(setpoint,float) or isinstance(setpoint,int)):
			command_string = "SETP{},{}\r".format(channel,setpoint)
		elif channel in range(1,5):
			command_string = "SETP{}?\r".format(channel)
		else:
			return 0

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def set_stop(self):
		"""
		Stop controller
		"""
		if self.simulate:
			return 0

		command_string = "STOP\r"
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_throttle(self, pvchannel):
		"""
		The query command asks the 8800 for the current channel throttle reading. The 8800
		sends the throttle value as a percentage.
		"""
		if self.simulate:
			return 0

		if pvchannel in range(1,9):
			command_string = "THTL{}?\r".format(pvchannel)
		else:
			return 0

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def print_version(self):
		"""
		Queries the 8800 for the version number of the display software.
		"""
		if self.simulate:
			return 0

		command_string = "VRSN?\r"
		self.tn.write(command_string.encode("ascii"))
		print(self.tn.read_some().decode("ascii").strip())

	def get_version(self):
		"""
		Queries the 8800 for the version number of the display software.
		"""
		if self.simulate:
			return 0

		command_string = "VRSN?\r"
		self.tn.write(command_string.encode("ascii"))
		return self.tn.read_some().decode("ascii").strip()

	def get_set_final_value(self, channel, value=None):
		"""
		This query command asks the 8800 for the current interval's final value for channel n (1-4).
		The 8800 sends a decimal value for the selected channel. The edit from hold operation
		command temporarily changes the current interval's final value.
		"""
		if self.simulate:
			return 0

		if channel in range(1,5) and (isinstance(value,float) or isinstance(value,int)):
			command_string = "FVAL{},{}\r".format(channel,value)
		elif channel in range(1,5):
			command_string = "FVAL{}?\r".format(channel)
		else:
			return 0

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_loops_left(self, loops=None):
		"""
		The query command asks the 8800 for the number of loops left to be executed for the current
		loop. On nested looping, the value is for the inside loop. The 8800 sends an integer to indicate
		the number of loops left. The edit from hold operation command temporarily changes the
		current interval's loop counter.
		"""
		if self.simulate:
			return 0

		if isinstance(loops,int):
			command_string = "LLFT{}\r".format(loops)
		else:
			command_string = "LLFT?\r"
			
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()


	def get_time_left(self, time=None):
		"""
		Queries the 8800 for the time left in the current interval. The edit from hold operation
		command temporarily changes the current interval's time left counter.
		time is a string in the format "hh:mm:ss"
		"""
		if self.simulate:
			return 0

		if isinstance(time, str):
			command_string = "TLFT{}\r".format(time)
		else:
			command_string = "TLFT?\r"
			
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()		


	def set_resume(self):
		"""
		Returns a program or test from hold mode to its run mode.
		"""
		if self.simulate:
			return 0

		command_string = "RESM\r"
		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_set_programming_interval(self,
		interval,
		fv1="",
		fv2="",
		fv3="",
		fv4="",
		dv1="",
		dv2="",
		dv3="",
		dv4="",
		hr_min_sec="",
		pgrp="",
		lp="",
		ni="",
		auxg1="",
		auxg2="",
		display_status_byte="",
		options="",
		channels=""):
		"""
		The query command asks for the interval string that initializes the program (INTV0) or for
		one of the program intervals (INTVn). During load program by value operations, send an
		INTV0? command, followed by an INTVn? command for every interval in your program. Use the
		PROGn? command to determine how many intervals you need to receive.

		The operation command sends an interval string to initialize the program (INTV0) or one of
		the program intervals (INTVn).
		"""
		if self.simulate:
			return 0

		# it's easier to write aux on & off in binary from left to right
		if auxg1: 
			if len(auxg1) > 3:
				auxg1 = int(auxg1[::-1],2)
		if auxg2: 
			if len(auxg2) > 3:
				auxg2 = int(auxg2[::-1],2)


		if int(interval) >= 0 and not (fv1 or fv2 or fv3 or fv4):
			options_list=["{}?".format(interval)]
		elif int(interval) >= 0:
			if int(interval) > 0:
				options_list = [interval,fv1,fv2,fv3,fv4,dv1,dv2,dv3,dv4,hr_min_sec,pgrp,lp,ni,
				auxg1,auxg2,display_status_byte,options]
			else:
				options_list = [interval,fv1,fv2,fv3,fv4,channels]

		config_str = ",".join([str(x) for x in options_list])
		command_string = "INTV{}".format(config_str)

		print(command_string)

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def get_set_prog(self, prog_name="", intervals=None):
		"""
		This command sets up the 8800 or host computer to load an entire program into the 8800's
		program memory. the query command receives the data string from the 8800, while the
		operation command sends the data string to the 8800.

		The query command sets up which program will be retrieved, and responds with the name
		of the program and the number of intervals in the program.

		The operation command creates the name and the number of intervals in the program.
		"""
		if self.simulate:
			return 0

		if prog_name and isinstance(intervals, int):
			command_string = "PROG{},{}\r".format(prog_name, intervals)
		elif prog_name:
			command_string = "PROG{}?\r".format(prog_name)
		elif intervals:
			command_string = "PROG{}?\r".format(intervals)
		else:
			command_string = "PROGn?\r"

		self.tn.write(command_string.encode("ascii"))
		# Wait a tiny bit so that there is time for the value to set.
		sleep(0.001)
		return self.tn.read_some().decode("ascii").strip()

	def ptc_on(self):
	    """
	    Queries the chamber and turns on PTC control
	    """
	    #PTC control is option 1
	    options = int(self.get_set_options())
	    if (options | 1) != options:
	        #make sure humidity and altitude are off
	        options = options & ~18
	        self.get_set_options(options | 1)

	def ptc_off(self):
	    """
	    Queries the chamber and turns off PTC control
	    """
	    #PTC control is option 1
	    options = int(self.get_set_options())
	    if (options & ~1) != options:
	        self.get_set_options(options & ~1)

	def humidity_on(self):
	    """
	    Queries the chamber and turns on humidity
	    """
	    #Humidity is option 2
	    options = int(self.get_set_options())
	    if (options | 2) != options:
	        #make sure PTC and altitude are off
	        options = options & ~17
	        self.get_set_options(options | 2)

	def humidity_off(self):
	    """
	    Queries the chamber and turns off humidity
	    """
	    #Humidity is option 2
	    options = int(self.get_set_options())
	    if (options & ~2) != options:
	        self.get_set_options(options & ~2)