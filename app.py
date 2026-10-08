from flask import Flask, render_template, request
from route_analysis import TransportNetwork

app = Flask(__name__)
network = TransportNetwork()

@app.route("/", methods=["GET", "POST"])
def index():
    stations = network.get_stations()
    stats = network.get_network_stats()
    
    path = None
    distance = None
    segments = None
    error = None
    selected_source = None
    selected_dest = None
    active_path = None
    
    # Read theme parameter from form or query string (defaults to dark)
    theme = request.values.get("theme", "dark")

    if request.method == "POST":
        selected_source = request.form.get("source")
        selected_dest = request.form.get("destination")

        if selected_source == selected_dest:
            error = "Source and destination cannot be identical."
        else:
            path, distance, segments, error = network.find_shortest_route(selected_source, selected_dest)
            if path:
                active_path = path

    graph_img = network.generate_visualization(active_path=active_path, theme=theme)

    return render_template(
        "index.html",
        stations=stations,
        stats=stats,
        path=path,
        distance=distance,
        segments=segments,
        error=error,
        selected_source=selected_source,
        selected_dest=selected_dest,
        graph_img=graph_img,
        theme=theme
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)