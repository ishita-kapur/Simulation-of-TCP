### Project Name: missionTCP
Project Description: Simulate the working of TCP to understand the Transport Layer Protocol

## Ishita Kapur, 1001753123
# CSE 5344, Fall 2019

# Tools and Softwares Used for Implementation:
	* Notepad++
	* Python 3.7.3
	* Command Prompt

# Assumptions:
	* Path costs between the nodes(routers and agents) remain constant.
	* Scripts are executed in the following order:
			- mission_tcp.py
			- jan.py
			- chan.py
			- ann.py
	* Mission 3 starts after Agent Chan is terminated, leaving only Jan and Ann on the mission.
	* Connection is established between Jan and Ann, Ann and Chan, and Chan and Jan.
	* There is no packet loss.
	* Dirctory Structure of `Logs` should be present before executing the scripts. Folders `Ann`, `Jan` and `Chan` need to be created withing the `Logs` folder prior to project execution.
		

# Steps to Execute:
	1.	Start command prompt. Navigate to the folder containing the scripts.
	2.	Repeat Step 1 three more times.
	3.	If environment variables are not set for python, set path of python in all the four terminal windows.
	4.	Execute the scripts by typing the following commands in specified order in the above four different terminals:
				i.	`python mission_tcp.py`
				ii. `python jan.py`
				iii.`python chan.py`
				iv. `python ann.py`
	5.	Logs can be viewed in the Logs folder. Packet flow along the paths through routers can be viewed on the terminal window.


Additional details of the project implementation have been described in the `implementation.txt` file