import struct
import curses
import signal
import sys
import threading
import time
import socket
from pythonosc.udp_client import SimpleUDPClient

def signal_handler(sig, frame):
    print("\nProgram stopped with Ctrl+C")
    sys.exit(0)

def send_osc_command(x, y, z, yaw, pitch, roll, client, lock, event, last_sent_time):
    with lock:
        last_sent_time["XYZ"] = time.time()
    
    try:
        client.send_message("/b/Master/PositionX", x)
        client.send_message("/b/Master/PositionY", y)
        # # client.send_message("/b/Master/PositionZ", z)
        client.send_message("/b/Master/SizeX", z)
        client.send_message("/b/Master/SizeY", z)
        client.send_message("/b/Master/RotoAngleX", pitch)
        client.send_message("/b/Master/RotoAngleY", yaw)
        client.send_message("/b/Master/RotoAngleZ", roll)
        print(f"OSC command sent: X={x:.2f}, Y={y:.2f}, Z={z:.2f}, Yaw={yaw:.2f}, Pitch={pitch:.2f}, Roll={roll:.2f}")
    except Exception as e:
        print(f"Error sending OSC command: {e}")
    finally:
        with lock:
            event.set()

def map_value(value, min_input, max_input, min_output, max_output):
    value = max(min_input, min(max_input, value))
    return min_output + (value - min_input) * (max_output - min_output) / (max_input - min_input)

def receive_udp_data(stdscr, client):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", 4242))
    udp_socket.settimeout(1.0)  # Set timeout to keep listening and allow Ctrl+C to work
    
    signal.signal(signal.SIGINT, signal_handler)
    
    last_x, last_y, last_z = None, None, None
    lock = threading.Lock()
    event = threading.Event()
    event.set()
    last_sent_time = {"XYZ": 0}  # Keep track of the last time all axes were sent
    
    while True:
        try:
            data, addr = udp_socket.recvfrom(48)
            unpacked_data = struct.unpack("dddddd", data)
            x, y, z, yaw, pitch, roll = unpacked_data
            
            stdscr.clear()
            stdscr.addstr(1, 2, "UDP OpenTrack Data:")
            stdscr.addstr(3, 2, f"X: {x:.2f}")
            stdscr.addstr(4, 2, f"Y: {y:.2f}")
            stdscr.addstr(5, 2, f"Z: {z:.2f}")
            stdscr.addstr(6, 2, f"Yaw: {yaw:.2f}")
            stdscr.addstr(7, 2, f"Pitch: {pitch:.2f}")
            stdscr.addstr(8, 2, f"Roll: {roll:.2f}")
            stdscr.refresh()
            
            mapped_x = map_value(x, -20.0, 20.0, -100.0, 100.0)
            mapped_y = map_value(y, -20.0, 20.0, -100.0, 100.0)
            # mapped_z = map_value(z, -20.0, 20.0, -100.0, 100.0)
            mapped_z = map_value(z, -40.0, 40.0, 100.0, 00.0)
            mapped_yaw = map_value(yaw, -90.0, 90.0, -180.0, 180.0)
            mapped_pitch = map_value(pitch, -90.0, 90.0, -360.0, 360.0)
            mapped_roll = map_value(roll, -90.0, 90.0, -180.0, 180.0)
            
            if (mapped_x, mapped_y, mapped_z) != (last_x, last_y, last_z):
                last_x, last_y, last_z = mapped_x, mapped_y, mapped_z
                event.clear()
                threading.Thread(target=send_osc_command, args=(mapped_x, mapped_y, mapped_z, mapped_yaw, mapped_pitch, mapped_roll, client, lock, event, last_sent_time), daemon=True).start()
        
        except socket.timeout:
            pass  # No data received, return to the loop to detect Ctrl+C
        except struct.error:
            stdscr.clear()
            stdscr.addstr(10, 2, "Unexpected data received:")
            stdscr.addstr(11, 2, f"Raw data: {data}")
            stdscr.refresh()

if __name__ == "__main__":
    from pythonosc.udp_client import SimpleUDPClient
    osc_client = SimpleUDPClient("127.0.0.1", 8000)
    curses.wrapper(receive_udp_data, osc_client)