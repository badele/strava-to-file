# strava-to-file

```
# Extract archive
# On Strava, create on your profile icon, my account, get started, Requests Your Archive 
mkdir -p ~/tmp/gpx ; cd ~/tmp/gpx 
# Copy you exported strava archive to ~/tmp/gpx 
unzip export_*.zip

# Summary
python summarize.py

# Convert
cd your_dezipped_strava_activities
python convert.py -d ~/private/projects/jesuisundesdeux/datas/traces -u $(basename $(pwd)
 ```