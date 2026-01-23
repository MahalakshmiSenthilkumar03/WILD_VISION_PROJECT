from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Wild Vision Dashboard</title>
<style>
body {
  margin:0; font-family:Arial;
  background:#d1fae5;
}
nav {
  background:#020617;
  color:white;
  padding:15px;
  display:flex;
  gap:20px;
}
nav a {
  color:white;
  cursor:pointer;
  text-decoration:none;
}
section { padding:20px; display:none; }
.active { display:block; }
.card {
  background:white;
  padding:15px;
  border-radius:10px;
  margin:10px 0;
}
</style>
<script>
function show(id){
 document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
 document.getElementById(id).classList.add('active');
}
</script>
</head>

<body>
<nav>
  <a onclick="show('live')">Live</a>
  <a onclick="show('history')">History</a>
  <a onclick="show('zones')">Zones</a>
</nav>

<section id="live" class="active">
<h2>Live Monitoring</h2>
<img src="/video" width="640">
</section>

<section id="history">
<h2>Poaching History</h2>
{% for e in events %}
<div class="card">
<b>{{e.label}}</b> | {{e.time}}<br>
Camera: {{e.camera}} | Zone: {{e.zone}}<br>
Risk: {{e.risk}}<br>
<img src="/{{e.image}}" width="200">
</div>
{% endfor %}
</section>

<section id="zones">
<h2>Zone Risk</h2>
<div class="card">INNER FOREST – HIGH RISK</div>
<div class="card">BUFFER ZONE – MEDIUM RISK</div>
<div class="card">OUTER ZONE – LOW RISK</div>
</section>
</body>
</html>
"""

@app.route("/")
def home():
    events = []
    try:
        with open("events.json") as f:
            events = json.load(f)
    except:
        pass
    return render_template_string(HTML, events=events)

@app.route("/video")
def video():
    return app.send_static_file("live.jpg")

if __name__ == "__main__":
    app.run(port=5000)
