import sys
sys.path.clear()
sys.path.extend(("", ".frozen", "/app"))


import app.main
app.main.main()
