#!/bin/bash
# 🌌 Aurora Symbolic Runtime Launcher (v1.0)

echo "🔧 Initializing symbolic runtime..."

mkdir -p static/js static/css static/data
pip install -r requirements.txt

echo "🚀 Launching Aurora ZIP Wizard GUI..."
bash start_aurora_gui_cloudhub.sh

if [ -f Aurora_GUI_CloudHub_DeployKit_v1.zip ]; then
  echo "�� Found DeployKit — unzipping..."
  unzip -o Aurora_GUI_CloudHub_DeployKit_v1.zip -d deploykit_tmp
  ls deploykit_tmp >> threadcore_start.log
fi

echo "📝 Logging session..."
echo "Launched: $(date)" > threadcore_start.log
echo "GUI: http://localhost:8080" >> threadcore_start.log

echo "✅ Symbolic runtime complete. Interface is now active."
