# Lab: Four-potentiometer robot arm digital twin

## Objectives

Read four analog sensors, transmit their readings over USB, convert readings into angles, and explain how pivot positions and axes determine linked arm motion.

## Equipment

Course Arduino board, four potentiometers, course controller parts, approved wiring harness, USB data cable, Arduino IDE, FreeCAD, and this repository. Follow the course-specific supply-voltage and wiring instructions.

## 1. Assemble and check the inputs

1. Assemble the supplied controller without forcing the shafts or bending potentiometer pins.
2. Disconnect USB before wiring. Use the instructor-approved circuit and common ground.
3. Connect the four wipers in order to A0 (base), A1 (shoulder), A2 (elbow), and A3 (wrist). Confirm the board permits the applied analog voltage.
4. Open `arduino/Arduino_To_Collab/Arduino_To_Collab.ino` in Arduino IDE. Choose the correct board and port, then upload.
5. Open Serial Monitor at 9600 baud. Turn each knob individually; expect four comma-separated integers from 0 to 1023 per line. Record the serial port and close Serial Monitor.

## 2. Launch FreeCAD

Follow the platform setup in `README.md`. Set `PORT` in `robot_arm.py` to your actual port, such as `COM3` on Windows. Keep all main files together, then use the appropriate launcher or run `RobotArm.FCMacro` inside FreeCAD.

### Portable FreeCAD on Windows

Download the stable Windows portable `.7z` package from https://www.freecad.org/downloads.php and extract the entire archive. Locate its actual `FreeCAD.exe` (often under `bin`; some releases place it at the top level).

In `Launch Robot Arm.bat`, remove `rem` from the example path setting and use your extracted executable path, for example:

```bat
set "FREECAD_EXE=C:\Tools\FreeCAD\bin\FreeCAD.exe"
```

Keep the robot project in a writable folder. If portable FreeCAD has no Python or pip, install pyserial into the project using the manual command in the README. Once dependencies are prepared, you can also open the macro directly in portable FreeCAD. Update `FREECAD_EXE` whenever you move FreeCAD. USB drivers or classroom permissions may still require IT setup. Windows portable operation has not been hardware-tested.

## 3. Demonstrate joint motion

Move each knob slowly. Identify its corresponding model joint. The fixed base stays in place, while the moving pedestal rotates. Explain why shoulder rotation carries both the elbow and wrist. Close the arm document to release the serial connection.

## 4. Calculate and adjust the mapping

```python
angle = minimum + reading / 1023 * (maximum - minimum)
```

For limits (-90, 90), readings 0 and 1023 give -90 and +90 degrees. Reading 512 gives approximately +0.088 degrees. Calculate the result for 256. With instructor approval, change one joint to (-45, 45), rerun the macro, and compare the travel. Reverse the limits to reverse its direction. Restore the approved settings afterward.

## 5. Explain the mechanical transformation

Locate `pivot`, `axis`, `rotation`, `offset`, and `parent` in `move_arm`. A pivot is a point, an axis is a direction, and the parent placement carries upstream motion. Explain what would happen if a pivot were misplaced or a downstream link did not inherit shoulder movement.

## Record and submit

| Input | Joint | Raw minimum | Raw maximum | Angle limits | Direction correct? |
| --- | --- | --- | --- | --- | --- |
| A0 | Base | | | | |
| A1 | Shoulder | | | | |
| A2 | Elbow | | | | |
| A3 | Wrist | | | | |

Provide a working-model screenshot, the table, the calculation for 256, and a short explanation of voltage-to-angle mapping and linked motion. Follow your instructor's submission requirements.

## Instructor checks before classroom release

Verify actual Arduino wiring and voltage, the Windows launcher on a classroom PC, model dimensions, pivot locations, angle ranges, and physical joint directions. The model is a kinematic visualization, without motor physics or collision enforcement. No smoothing is applied.
