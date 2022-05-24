git remote set-url origin git@github.com:xtevenx/ProRankings
git fetch --all && git reset --hard origin/master
python3 -m pip install -r requirements.txt --user || python3 -m pip install -r requirements.txt
python3 main.py
git add index.html assets/js/chart-config.js
git commit -m "Update rating charts for `date '+%Y-%m-%d %T'`." && git push
