import base64
import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


class TransportNetwork:
    def __init__(self, csv_path="data/transport_routes.csv"):
        self.csv_path = csv_path
        self.graph = nx.Graph()
        
        self.geo_positions = {
            # North & Airport Sector
            "KIA Airport": (6.0, 14.5),
            "Yelahanka": (5.5, 11.0),
            "Hebbal": (4.5, 8.2),
            "Nagawara": (6.5, 8.0),
            "Kalyan Nagar": (8.0, 7.5),
            "Banaswadi": (7.5, 6.2),
            "Ramamurthy Nagar": (9.5, 7.0),

            # North-West & NH48 Spine
            "Nelamangala": (-4.0, 11.5),
            "Madavara": (-2.5, 10.5),
            "Nagasandra": (-1.5, 9.8),
            "Dasarahalli": (-0.8, 9.0),
            "Jalahalli": (0.0, 8.2),
            "Peenya": (1.0, 7.5),
            "Yeshwanthpur": (2.2, 6.8),
            "Malleswaram": (3.2, 5.5),

            # Central Core
            "Majestic": (4.0, 4.8),
            "Shivajinagar": (5.4, 5.2),
            "MG Road": (6.0, 4.6),
            "City Market": (3.8, 3.8),
            "Chamrajpet": (2.8, 3.4),
            "Lalbagh": (4.2, 3.0),
            "Basavanagudi": (3.2, 2.5),

            # West & South-West
            "Rajajinagar": (2.4, 4.8),
            "Vijayanagar": (1.2, 3.8),
            "Nayandahalli": (0.5, 2.2),
            "Rajarajeshwari Nagar": (-0.5, 1.0),
            "Kengeri": (-1.5, -0.2),

            # East & IT Corridors
            "Tin Factory": (8.8, 5.5),
            "KR Puram": (10.0, 5.8),
            "Mahadevapura": (10.5, 4.8),
            "Indiranagar": (7.2, 4.5),
            "Domlur": (7.4, 3.6),
            "HAL": (8.8, 3.6),
            "Marathahalli": (10.5, 3.6),
            "Kundalahalli": (12.0, 4.0),
            "ITPL": (13.0, 4.5),
            "Whitefield": (14.0, 4.5),
            "Kadugodi": (15.2, 4.8),
            "Bellandur": (9.8, 2.4),
            "Devarabisanahalli": (10.4, 1.8),

            # South & Outer Ring Road
            "Dairy Circle": (4.6, 2.2),
            "Koramangala": (6.4, 2.4),
            "Jayanagar": (3.6, 1.8),
            "Banashankari": (2.6, 1.2),
            "Kumaraswamy Layout": (2.0, 0.2),
            "ISRO Layout": (1.2, -0.5),
            "JP Nagar": (3.8, 0.6),
            "BTM Layout": (5.0, 1.0),
            "Silk Board": (6.5, 1.0),
            "HSR Layout": (7.8, 1.2),
            "Sarjapur Road": (9.0, 1.0),
            "Carmelaram": (10.8, 0.4),
            "Dommasandra": (12.2, -0.4),
            "Sarjapur": (13.8, -1.2),

            # Chandapura - Dommasandra (CD Road) Corridor
            "Heelalige Cross": (8.8, -3.2),
            "Ramasagara": (9.4, -2.6),
            "Singena Agrahara": (10.0, -2.0),
            "Muthanallur Cross": (10.8, -1.4),
            "Chokkasandra Cross": (11.5, -0.9),

            # Bannerghatta South Corridor
            "Bannerghatta Road": (4.2, -0.4),
            "Meenakshi Mall": (4.0, -1.5),
            "Gottigere": (3.8, -2.6),
            "Bannerghatta": (3.5, -4.2),

            # Hosur Highway Spine & Anekal
            "Electronic City": (6.8, -0.8),
            "Hebbagodi": (7.0, -1.8),
            "Bommasandra": (7.2, -2.8),
            "Jigani": (4.8, -3.2),
            "Chandapura": (7.8, -3.8),
            "Surya City": (7.4, -4.6),
            "Iggalur": (7.1, -5.3),
            "Ramakrishnapura": (6.8, -6.0),
            "Marsur Gate": (6.5, -6.7),
            "Byagadadenahalli": (6.2, -7.4),
            "Karpur Gate": (5.9, -8.1),
            "Anekal": (5.6, -9.0),
            "Attibele": (11.0, -4.8)
        }
        self.load_network()

    def load_network(self):
        if not os.path.exists(self.csv_path):
            return

        df = pd.read_csv(self.csv_path)
        df.columns = [c.strip() for c in df.columns]

        for _, row in df.iterrows():
            bus = row.get("bus_number")
            bus_str = str(bus).strip() if (pd.notna(bus) and str(bus).strip()) else "BMTC Feeder"
            self.graph.add_edge(
                str(row["source"]).strip(),
                str(row["destination"]).strip(),
                weight=float(row["distance"]),
                bus_number=bus_str
            )

    def get_stations(self):
        return sorted(list(self.graph.nodes()))

    def get_network_stats(self):
        degrees = dict(self.graph.degree())
        sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        hubs = sorted_degrees[:3] if len(sorted_degrees) >= 3 else sorted_degrees
        
        return {
            "total_stations": self.graph.number_of_nodes(),
            "total_connections": self.graph.number_of_edges(),
            "connected_components": nx.number_connected_components(self.graph) if len(self.graph) > 0 else 0,
            "top_hubs": hubs
        }

    def find_shortest_route(self, source, destination):
        if source not in self.graph or destination not in self.graph:
            return None, None, None, "Invalid station selected."

        if not nx.has_path(self.graph, source, destination):
            return None, None, None, f"No connected path exists between {source} and {destination}."

        path = nx.shortest_path(self.graph, source=source, target=destination, weight="weight")
        distance = nx.shortest_path_length(self.graph, source=source, target=destination, weight="weight")

        segments = []
        for u, v in zip(path[:-1], path[1:]):
            edge_data = self.graph.get_edge_data(u, v) or {}
            segments.append({
                "from": u,
                "to": v,
                "distance": edge_data.get("weight", 0.0),
                "bus_number": edge_data.get("bus_number", "BMTC Feeder")
            })

        return path, round(distance, 2), segments, None

    def generate_visualization(self, active_path=None, theme="dark"):
        """Generates clear, readable transit graph matching light/dark modes."""
        is_dark = (theme == "dark")
        bg_color = "#0B132B" if is_dark else "#F8FAFC"
        edge_base = "#1E293B" if is_dark else "#CBD5E1"
        node_base = "#1E293B" if is_dark else "#E2E8F0"
        node_border = "#64748B" if is_dark else "#94A3B8"
        label_text = "#E2E8F0" if is_dark else "#1E293B"
        label_bg = "#0F172A" if is_dark else "#FFFFFF"
        label_edge = "#334155" if is_dark else "#E2E8F0"

        fig, ax = plt.subplots(figsize=(16, 13), facecolor=bg_color)
        ax.set_facecolor(bg_color)

        default_pos = nx.spring_layout(self.graph, seed=42)
        pos = {}
        for node in self.graph.nodes():
            if node in self.geo_positions:
                pos[node] = self.geo_positions[node]
            else:
                pos[node] = (default_pos[node][0] * 10, default_pos[node][1] * 10)

        # 1. Base network tracks
        nx.draw_networkx_edges(
            self.graph, pos, ax=ax,
            edge_color=edge_base,
            width=2.0,
            alpha=0.8
        )

        # 2. Base stations
        nx.draw_networkx_nodes(
            self.graph, pos, ax=ax,
            node_color=node_base,
            node_size=280,
            edgecolors=node_border,
            linewidths=1.2
        )

        # 3. Active Path
        active_set = set(active_path) if active_path else set()
        if active_path and len(active_path) > 1:
            path_edges = list(zip(active_path[:-1], active_path[1:]))

            nx.draw_networkx_edges(
                self.graph, pos, ax=ax,
                edgelist=path_edges,
                edge_color="#2563EB",
                width=4.5
            )

            source_node = [active_path[0]]
            dest_node = [active_path[-1]]
            intermediate_nodes = active_path[1:-1]

            # Green Start
            nx.draw_networkx_nodes(
                self.graph, pos, ax=ax,
                nodelist=source_node,
                node_color="#10B981",
                node_size=550,
                edgecolors="#FFFFFF",
                linewidths=2.0
            )

            # Amber Transfers
            if intermediate_nodes:
                nx.draw_networkx_nodes(
                    self.graph, pos, ax=ax,
                    nodelist=intermediate_nodes,
                    node_color="#F59E0B",
                    node_size=380,
                    edgecolors="#FFFFFF",
                    linewidths=1.5
                )

            # Red End
            nx.draw_networkx_nodes(
                self.graph, pos, ax=ax,
                nodelist=dest_node,
                node_color="#EF4444",
                node_size=550,
                edgecolors="#FFFFFF",
                linewidths=2.0
            )

        # 4. Readable Labels with subtle bounding background (effortless to read)
        for node, (x, y) in pos.items():
            is_active = node in active_set
            
            # Subtle badge styling
            bbox_props = dict(
                boxstyle="round,pad=0.25",
                fc="#1E293B" if (is_dark and is_active) else ("#DBEAFE" if (not is_dark and is_active) else label_bg),
                ec="#3B82F6" if is_active else label_edge,
                lw=1.2 if is_active else 0.8,
                alpha=0.95
            )

            ax.text(
                x, y + 0.32,
                s=node,
                fontsize=7.5 if is_active else 6.5,
                fontweight="bold" if is_active else "medium",
                color="#FFFFFF" if (is_dark and is_active) else ("#1D4ED8" if (not is_dark and is_active) else label_text),
                ha="center",
                va="bottom",
                bbox=bbox_props,
                zorder=10 if is_active else 5
            )

        ax.axis("off")
        fig.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode("utf-8")