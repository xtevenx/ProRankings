git fetch --all && git reset --hard origin/master
python3 -m pip install -r requirements.txt --user || python3 -m pip install -r requirements.txt
python3 main.py
git add data/output_bar.png data/output_tourney.png data/output_line.png
git add index.html assets/js/chart-config.js
git commit -m "Update rating charts for `date '+%Y-%m-%d %H:00:00'`." && git push
