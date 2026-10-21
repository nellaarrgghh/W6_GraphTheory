import networkx as nx

def solve_dcpp(G: nx.DiGraph, start_node):
    """
    Solves the Directed Chinese Postman Problem (DCPP) on a NetworkX DiGraph.
    """
    out_deg = dict(G.out_degree())
    in_deg = dict(G.in_degree())
    
    supply = {}
    demand = {}
    
    for node in G.nodes():
        diff = out_deg.get(node, 0) - in_deg.get(node, 0)
        if diff > 0:
            supply[node] = diff
        elif diff < 0:
            demand[node] = -diff

    G_aug = G.copy()
    
    if supply and demand:
        flow_net = nx.DiGraph()
        source, sink = "super_source", "super_sink"
        flow_net.add_node(source)
        flow_net.add_node(sink)
        
        total_supply = sum(supply.values())
        for s, qty in supply.items():
            flow_net.add_edge(source, s, capacity=qty, weight=0)
        for d, qty in demand.items():
            flow_net.add_edge(d, sink, capacity=qty, weight=0)
            
        lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='length'))
        paths = dict(nx.all_pairs_dijkstra_path(G, weight='length'))
        
        for s in supply.keys():
            for d in demand.keys():
                if d in lengths.get(s, {}):
                    flow_net.add_edge(s, d, capacity=float('inf'), weight=lengths[s][d])
                    
        try:
            flow_dict = nx.min_cost_flow(flow_net, demand={sink: total_supply})
            for s in supply.keys():
                if s in flow_dict:
                    for d, flow_val in flow_dict[s].items():
                        if d in demand.keys() and flow_val > 0:
                            path = paths[s][d]
                            for i in range(len(path) - 1):
                                u, v = path[i], path[i+1]
                                edge_data = G.get_edge_data(u, v)
                                if edge_data:
                                    key = list(edge_data.keys())[0]
                                    G_aug.add_edge(u, v, **edge_data[key])
        except Exception:
            pass

    # Find Eulerian circuit
    try:
        route_edges = list(nx.eulerian_circuit(G_aug, source=start_node))
    except nx.NetworkXError:
        route_edges = [(u, v) for u, v in G_aug.edges()]
        
    return G_aug, route_edges