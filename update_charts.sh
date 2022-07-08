git fetch --depth=1
git reset --hard origin/master
python3 -m pip install -r requirements.txt
python3 main.py
git add index.html assets/js/chart-config.js
git diff-index --quiet origin/master || git commit -m "Update rating charts for `date '+%Y-%m-%d %T'`."
git push
