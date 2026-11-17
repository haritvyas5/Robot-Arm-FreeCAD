"""Four potentiometers → four joint angles → a FreeCAD arm."""
import sys                         # Lets FreeCAD find the installed USB serial library.
from pathlib import Path           # Handles paths to the model and library.

FOLDER = Path(__file__).resolve().parent  # This project's folder.
PORT = ""                          # Windows: "COM3"; Mac: "/dev/cu.usbmodem1101". Use your board's port.
BAUD_RATE = 9600                    # Must match Serial.begin(9600) on the Arduino.

# A0 → base, A1 → shoulder, A2 → elbow, A3 → wrist.
# Each row identifies a model part, its hinge position (mm), its rotation axis,
# and its angle range (degrees). Pivots and limits still need physical calibration.
JOINTS = [
    {"part": "Link0", "pivot": (0, 0, 5.775), "axis": (0, 0, 1), "angles": (-90, 90)},
    {"part": "Link3", "pivot": (0, 0.2, 22.8), "axis": (1, 0, 0), "angles": (-90, 90)},
    {"part": "Link4", "pivot": (0, -9.3, 51.13), "axis": (1, 0, 0), "angles": (-90, 90)},
    {"part": "Link1", "pivot": (0, 21.0, 49.737), "axis": (1, 0, 0), "angles": (-90, 90)},
]

connection = None                  # No Arduino connection exists yet.
timer = None                       # No repeating update timer exists yet.


# Check one complete Arduino message.
def read_values(line):
    fields = line.split(",")        # Split a message such as '0,512,900,1023'.
    if len(fields) != 4:            # Every message must contain four readings.
        return None                # Ignore incomplete or incorrectly formatted messages.
    readings = []                  # Start an empty list for the checked readings.
    try:                           # Handle text that cannot be converted to a number.
        for field in fields:       # Check each of the four pieces of text.
            reading = int(field)   # Convert the text to a whole number.
            if reading < 0 or reading > 1023:  # Arduino readings must fit this range.
                return None        # Ignore a message with an invalid reading.
            readings.append(reading)  # Add the valid reading to our list.
    except ValueError:             # A piece of text was not a whole number.
        return None                # Ignore that message instead of stopping the program.
    return readings                # Return the four valid sensor readings.


# Convert a sensor reading into a mechanical joint angle.
def to_angle(reading, limits):
    minimum, maximum = limits      # Get this joint's two angle limits.
    return minimum + reading / 1023 * (maximum - minimum)  # Scale the sensor range.


# Apply the four angles while keeping the joint chain connected.
def move_arm(angles):
    parent = App.Placement()        # Start with no movement inherited from another joint.
    for index in range(4):         # Work from the base toward the wrist.
        joint = JOINTS[index]      # Get this joint's geometry and angle limits.
        part = document.getObject(joint["part"])  # Find its moving part in FreeCAD.
        pivot = App.Vector(*joint["pivot"])       # Convert the hinge coordinates to a vector.
        axis = App.Vector(*joint["axis"])         # Convert the rotation direction to a vector.
        rotation = App.Rotation(axis, angles[index])  # Rotate by this joint's angle.
        offset = pivot - rotation.multVec(pivot)  # Keep the hinge fixed during rotation.
        turn = App.Placement(offset, rotation)   # Combine this rotation and offset.
        part.Placement = parent.multiply(turn)   # Include all upstream joint movements.
        parent = part.Placement    # Carry the accumulated movement into the next joint.


# Read the latest complete message and update the model.
def update_arm():
    global buffer                  # Keep unfinished bytes between timer calls.
    if document_name not in App.listDocuments():  # Stop when the model is closed.
        stop()                     # Release the serial port and stop the timer.
        return                     # Do not try to move a closed model.
    try:                           # The board may be unplugged between updates.
        buffer += connection.read(4096)  # Read available bytes without waiting for more.
    except (serial.SerialException, OSError) as error:  # Catch a USB connection failure.
        stop()                     # Stop further reads and release the connection.
        App.Console.PrintError(f"Arduino disconnected: {error}\n")  # Explain the failure.
        return                     # End this update after a disconnection.
    lines = buffer.split(b"\n")    # Separate complete messages at newline characters.
    buffer = lines.pop()           # Save the final, possibly unfinished message.
    if len(buffer) > 256:          # Avoid keeping an endlessly growing malformed message.
        buffer = b""               # Discard that unfinished message.
    readings = None                # No valid complete message has been found yet.
    for line in lines:             # Inspect every complete message received this tick.
        values = read_values(line.decode("ascii", errors="replace"))  # Decode and check it.
        if values is not None:     # Ignore bad messages; keep the latest good one.
            readings = values      # Replace any older reading from this tick.
    if readings is None:           # With no new valid readings, the pose stays unchanged.
        return                     # There is no need to move the model again.
    angles = []                    # Build the four requested joint angles.
    for index in range(4):         # Match each potentiometer with its joint.
        angle = to_angle(readings[index], JOINTS[index]["angles"])  # Convert reading to angle.
        angles.append(angle)       # Store the calculated angle.
    move_arm(angles)                # Move directly to those angles, without easing.


# Stop updates and release the USB serial connection.
def stop():
    if timer is not None:          # A timer may not have been created yet.
        timer.stop()               # Prevent further update calls.
    if connection is not None:     # A serial connection may not have been opened yet.
        connection.close()         # Release the Arduino port for another run or program.


# Open the model and start reading the chosen Arduino port.
def launch(port=PORT):
    global App, serial, document, document_name, connection, timer, buffer  # Shared run state.
    import FreeCAD as App          # Loads document, vector, and rotation functions.
    import FreeCADGui as Gui       # Loads functions for the model's 3D view.
    from PySide import QtCore      # Provides a timer that works with FreeCAD's interface.
    sys.path.append(str(FOLDER / ".dependencies"))  # Library installed by the Windows launcher.
    sys.path.append(str(FOLDER / ".venv" / "Lib" / "site-packages"))  # Windows virtual environment.
    for packages in FOLDER.glob(".venv/lib/python*/site-packages"):  # Mac/Linux virtual environment.
        sys.path.append(str(packages))  # Reuse its pure-Python serial library.
    try:                           # Give a clear message if pyserial has not been installed.
        import serial              # Provides the USB serial connection on either system.
    except ImportError:             # The serial library is missing from all these locations.
        App.Console.PrintError("Install pyserial as described in README.md, then rerun the macro.\n")
        return                     # Do not continue without the required library.
    stop()                         # Release any connection and timer from a previous run.
    buffer = b""                   # Begin with an empty incoming message buffer.
    document = App.openDocument(str(FOLDER / "RobotArm.FCStd"))  # Open the arm model.
    document_name = document.Name  # Remember its name so closure can be detected safely.
    Gui.activeDocument().activeView().viewAxonometric()  # Choose an angled 3D view.
    Gui.activeDocument().activeView().fitAll()           # Fit the whole arm on screen.
    if not port:                   # Require an explicit Arduino port for this lesson.
        App.Console.PrintError("Set PORT at the top of robot_arm.py, then rerun the macro.\n")
        return                     # Leave the model open without attempting a connection.
    try:                           # Opening the selected port might fail.
        connection = serial.Serial(port, BAUD_RATE, timeout=0)  # Nonblocking USB reads.
        connection.reset_input_buffer()  # Discard old input left over when the port opens.
    except serial.SerialException as error:  # Report an unavailable or busy serial port.
        stop()                     # Close the connection if setup only partly succeeded.
        App.Console.PrintError(f"Cannot open Arduino: {error}\n")  # Show the opening error.
        return                     # Do not start updates without a working connection.
    timer = QtCore.QTimer()        # Create the repeating update timer.
    timer.timeout.connect(update_arm)  # Call update_arm whenever the timer ticks.
    timer.start(16)                # Request an update every 16 milliseconds.
