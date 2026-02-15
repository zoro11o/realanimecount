from flask import Flask, render_template, request
from analyzer import get_unique_franchises
import os
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    franchises = None
    count = None
    username = None
    total_watch_time = None

    if request.method == "POST":
        username = request.form.get("username")

        if username:
            franchises, total_watch_time = get_unique_franchises(username)
            count = len(franchises)

    return render_template(
        "index.html",
        franchises=franchises,
        count=count,
        username=username,
        total_watch_time=total_watch_time
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

