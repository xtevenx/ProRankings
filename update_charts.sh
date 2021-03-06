git fetch --all && git reset --hard origin/master
python3 -m pip install -r requirements.txt --user || python3 -m pip install -r requirements.txt
python3 main.py
git diff --exit-code --quiet data/output_bar.png || git add data/output_bar.png
git diff --exit-code --quiet data/output_tourney.png || git add data/output_tourney.png
git diff --exit-code --quiet data/output_line.png || git add data/output_line.png
git commit -m "Update rating charts for `date '+%Y-%m-%d %H:00:00'`." && git push
