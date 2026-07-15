#!/bin/bash
# recalc.sh — rerunnable LibreOffice full-recalc of the rev4 books (+ rev3 reference).
# Starts a throwaway headless soffice UNO listener with a FRESH profile in a
# SPACE-FREE temp dir (a space in the -env:UserInstallation URL crashes soffice
# with an uncaught RuntimeException and leaves a `safemode` marker), runs
# recalc_uno.py through the system python3 (python3-uno), then shuts it down.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROF="$(mktemp -d /tmp/lorecalc.XXXXXX)"
mkdir -p "$PROF/lohome/user"
cat > "$PROF/lohome/user/registrymodifications.xcu" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
EOF
soffice --headless --norestore --nologo \
  -env:UserInstallation="file://$PROF/lohome" \
  --accept="socket,host=127.0.0.1,port=2002;urp;" >"$PROF/soffice.log" 2>&1 &
SOF=$!
trap 'kill $SOF 2>/dev/null || true; rm -rf "$PROF"' EXIT
for i in $(seq 1 30); do
  python3 - <<'PY' 2>/dev/null && break || sleep 1
import uno
lc = uno.getComponentContext()
r = lc.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', lc)
r.resolve('uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext')
PY
done
python3 "$HERE/recalc_uno.py"
