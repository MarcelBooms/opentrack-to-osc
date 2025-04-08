# OpenTrack to OSC for Pangolin Beyond

This script enables real-time control of position and rotation in **Pangolin Beyond** using **headtracking data** via the **OpenTrack** standard. It receives UDP packets with tracking data (e.g. from an iPhone running [SmoothTrack](https://apps.apple.com/us/app/smoothtrack/id1531986830)) and translates this data into OSC commands that Beyond can interpret.

## 🎯 Purpose

The goal is to map 6DOF headtracking input — position (`x`, `y`, `z`) and rotation (`yaw`, `pitch`, `roll`) — to visual transformations in Pangolin Beyond during a liveshow.

This is especially useful for immersive and dynamic control of laser visuals based on head movement.

## 🛠 How It Works

- Listens on **UDP port 4242** for OpenTrack 6DOF data (`double`-precision floats).
- Transforms incoming values to match Beyond's expected value ranges.
- Sends the transformed data as OSC commands to Pangolin Beyond via local loopback (`127.0.0.1`).
- Uses Python's `curses` for basic terminal-based monitoring.

## 🧪 Tested With

- **SmoothTrack** (iOS)
  - IP: IP of the machine running this script
  - Port: `4242`
  - Protocol: OpenTrack UDP

Any headtracking system that supports OpenTrack over UDP will likely work.

## 📦 Requirements

- Python 3.8+
- Dependencies:
  ```bash
  pip install python-osc
  ```

## 🚀 Usage

1. Run the script:
   ```bash
   python opentrack_to_osc.py
   ```

2. Configure your headtracking app to send UDP packets to your computer's IP address on **port 4242**.

3. The script will:
   - Display the received OpenTrack data in the terminal.
   - Convert values using the adjustable `mapped_*` variables.
   - Send them as OSC messages to Pangolin Beyond.

## 🎚 Customization

You can fine-tune the input and output mapping ranges by editing these lines:

```python
mapped_x = map_value(x, -40.0, 40.0, 0, 255.0)
mapped_y = map_value(y, -20.0, 20.0, -100.0, 100.0)
mapped_z = map_value(z, -40.0, 40.0, -200.0, 200.0)
mapped_yaw = map_value(yaw, -40.0, 40.0, -100.0, 100.0)
mapped_pitch = map_value(pitch, -20.0, 20.0, -100.0, 100.0)
mapped_roll = map_value(roll, -40.0, 40.0, -180.0, 180.0)
```

Adjust these ranges depending on the expected range of head movement and Beyond's response.

## 📌 Notes

- OSC is sent to `127.0.0.1:8000` — make sure Pangolin Beyond is configured to listen for OSC on this port.
- This is an **early version** — UI/UX improvements, configuration options, and error handling are still in development.

## 📋 To Do

- Config file for mapping ranges
- GUI for live tuning of mappings
- OSC target IP/port selection
- Better error handling for malformed packets

---

🧠 Made for creative show control with live headtracking and Pangolin lasers.  
🎛✨