# Robot Arm Digital Twin — FreeCAD

## Run the lesson

1. Upload `arduino/Arduino_To_Collab/Arduino_To_Collab.ino` with Arduino IDE, using the course-approved A0–A3 wiring. Connect the board by USB and close Arduino Serial Monitor.
2. Set `PORT` near the top of `robot_arm.py` to the Arduino's serial port (for example `COM3` on Windows or `/dev/cu.usbmodem1101` on Mac). Arduino IDE's Tools → Port menu can show its name.
3. On Mac, double-click **Launch Robot Arm.command**; on Windows use **Launch Robot Arm.bat**. Alternatively, open `RobotArm.FCMacro` in FreeCAD and choose **Macro → Execute Macro**.

The model opens even if PORT has not been set. Connection errors appear in FreeCAD's Report view. Rerun the macro after changing a setting or reconnecting the board.


## Windows setup (real Arduino)

1. Install the Windows version of [FreeCAD](https://www.freecad.org/downloads.php). The code uses FreeCAD's Python interpreter, not a standalone Python window.
2. Copy the project to a writable folder on the Windows PC. Keep `robot_arm.py`, `RobotArm.FCStd`, `RobotArm.FCMacro`, and `Launch Robot Arm.bat` together. Do not copy the Mac `.venv`, `runtime`, or `FreeCAD.dmg`; they are not Windows installations. The Mac launcher is not required on Windows.
3. Connect the Arduino. Check Arduino IDE **Tools → Port** or Windows Device Manager **Ports (COM & LPT)** for its actual port. Set `PORT = "COM3"` in `robot_arm.py`, replacing COM3 with that port. Close Serial Monitor before launching the twin. If the board does not appear, check its data cable and the board manufacturer's USB driver instructions.
4. Double-click **Launch Robot Arm.bat**. It finds FreeCAD in common installation folders or on PATH. For a portable/custom installation, edit the commented `FREECAD_EXE` setting in the batch file and remove `rem` from that line.
5. On the first run, the launcher downloads **pyserial 3.5** into the project's `.dependencies` folder. It tries FreeCAD's bundled `python.exe`; if that is absent, it uses `py -3`. Internet access is required for that first installation. If neither interpreter is available, install Python 3 with the Windows `py` launcher or prepare `.dependencies` manually as below.

Manual dependency installation from Command Prompt in the project folder:

```bat
py -3 -m pip install --target ".dependencies" "pyserial==3.5"
```

If `py` is unavailable but `python` runs your installed Python 3, use `python -m pip` instead. If FreeCAD's bundled Python has no pip, this manual route also works. Once `.dependencies` is prepared, the launcher does not need a separate Python installation or internet access. The main code also recognizes a Windows virtual environment's `.venv\Lib\site-packages` when running the macro directly.

The `.bat` passes the macro to FreeCAD using its documented [command-line macro workflow](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/How_to_install_macros.md). pyserial provides Windows serial support; see its [installation instructions](https://pyserial.readthedocs.io/en/latest/pyserial.html). Windows execution and physical COM-port behavior have not been tested on this Mac.

## Read robot_arm.py

The file uses ordinary functions and loops, with line explanations. There is no class, automatic port detection, smoothing, or stale-input clock.

- **JOINTS:** identifies each moving part, hinge position, rotation axis and angle limits. The row order is A0 base, A1 shoulder, A2 elbow, A3 wrist.
- **read_values:** accepts messages containing four integers from 0 to 1023.
- **to_angle:** scales a potentiometer reading into a joint angle.
- **move_arm:** rotates each part around its hinge and inherits movement from the previous joint.
- **update_arm:** reads complete messages, converts the latest valid readings into angles, and moves the model directly.
- **stop / launch:** handle opening and closing the connection and starting FreeCAD's timer.

The key electronics calculation is:

`angle = minimum + reading / 1023 * (maximum - minimum)`

The key mechanical idea is that each joint rotates about a pivot and axis, while inheriting all upstream motion. Changing the shoulder therefore moves the elbow and wrist as well.

## Why a little USB handling remains

Arduino sends lines such as `512,800,200,600` at 9600 baud. USB can deliver a message in several chunks, so unfinished bytes are saved until a newline arrives. Invalid messages are ignored. Reads are nonblocking, so FreeCAD does not freeze while waiting for the board. The timer requests an update every 16 ms; actual timing varies.

Without a new valid message, the model simply stays in its previous pose. Closing the model or unplugging the board stops the serial updates. There is no automatic reconnection.

## Files and limits

Three files are needed: `robot_arm.py` (code/settings), `RobotArm.FCStd` (geometry), and `RobotArm.FCMacro` (entry point). The launcher is optional. On Mac, prepare a local `.venv` for pyserial; on Windows, the launcher prepares `.dependencies`; the installed FreeCAD supplies the CAD and timer functions. No cloud API is used.

Pivots, assumed model scale and angle limits still need physical calibration. This is a mesh-based kinematic model, without motor physics or collision enforcement. Reverse a row's angle limits to reverse its control direction.

Original model/sketch: https://github.com/haritvyas5/Robot-Arm; MIT license retained in `LICENSE`. The sensor parsing and mapping checks are in `tests/`.

```sh
.venv/bin/python -m unittest discover -s tests -v
```


## Mac first-time setup

Install FreeCAD into `/Applications/FreeCAD.app`. With Python 3 installed, open Terminal in this repository and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Set your serial port, then run `Launch Robot Arm.command`. The Arduino IDE Serial Monitor must be closed before either launcher runs.

## Attribution and license

The Arduino sketch and arm geometry come from [haritvyas5/Robot-Arm](https://github.com/haritvyas5/Robot-Arm). The FreeCAD model was made by separating the original STL into five components; source CAD mates and feature history were not imported. The original MIT copyright notice is retained in `LICENSE`. This repository supplies the separate local FreeCAD control implementation and Windows/Mac launchers.

Mac serial-emulation checks passed during development. Real Arduino operation, physical calibration, and Windows execution still require verification.


## Portable FreeCAD on Windows

1. Download the official Windows portable `.7z` archive from [FreeCAD releases](https://github.com/FreeCAD/FreeCAD/releases) and extract the entire archive.
2. Locate `FreeCAD.exe` in the extracted folder (often inside `bin`; the layout can vary).
3. Open `Launch Robot Arm.bat` in a text editor and uncomment the `FREECAD_EXE` setting. Set it to the actual executable path, for example:

```bat
set "FREECAD_EXE=C:\Tools\FreeCAD\bin\FreeCAD.exe"
```

4. Keep this project in a writable folder, set `PORT` in `robot_arm.py` to the Arduino COM port, close Arduino Serial Monitor, then double-click the batch launcher.
5. The launcher installs pyserial into the project’s `.dependencies` folder on first use. If the portable package has no usable Python installer, install Python 3 and run this command from the project folder:

```bat
py -3 -m pip install --target .dependencies pyserial==3.5
```

If you move the portable FreeCAD folder, update `FREECAD_EXE`. Alternatively, open the portable FreeCAD application and run `RobotArm.FCMacro` through Macro → Macros after installing the dependency. Portable Windows operation has not yet been tested with physical hardware.

### macOS ZIP downloads

If the command launcher is not executable after downloading the repository ZIP, open Terminal in the project folder and run:

```sh
chmod +x "Launch Robot Arm.command"
```
