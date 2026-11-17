#!/bin/zsh
cd "${0:A:h}"
FREECAD_RUNTIME='/Applications/FreeCAD.app/Contents/Resources'
if [[ ! -x "$FREECAD_RUNTIME/bin/freecad" ]]; then
  print 'FreeCAD was not found in /Applications/FreeCAD.app.'
  exit 1
fi
export PYTHONHOME="$FREECAD_RUNTIME"
export PYTHONPATH="$FREECAD_RUNTIME"
export LD_LIBRARY_PATH="$FREECAD_RUNTIME/lib"
exec "$FREECAD_RUNTIME/bin/freecad" "$PWD/RobotArm.FCMacro"
