import numpy as np
import h5py
import sqlite3
import os
import networkx as nx
import matplotlib.pyplot as plt

os.mkdir('DataBase')


# Przenoszenie danych z hdf5 do SQLite
def make_convert():
    with h5py.File('task_data.hdf5', 'r') as file:
        results_folder = list(file.get('results'))
        np.set_printoptions(precision=20)
        os.chdir('DataBase')
        for i, folder_name in enumerate(results_folder):

            os.mkdir(folder_name)
            os.chdir(folder_name)
            nodes = np.array(file.get('results').get(folder_name).get('nodes'))
            gens = np.array(file.get('results').get(folder_name).get('gens'))
            branches = np.array(file.get('results').get(folder_name).get('branches'))

            con = sqlite3.connect('data.db')
            cur = con.cursor()

            n = """
            CREATE TABLE {table_name} (
                node_id NUMERIC,
                node_type NUMERIC,
                demand [MW] NUMERIC)
            """
            cur.execute(n.format(table_name='nodes'))
            for node in nodes:
                cur.execute("INSERT INTO nodes VALUES(?, ?, ?)", (node[0], node[1], node[2]))

            g = """
            CREATE TABLE {table_name} (
                node_id NUMERIC,
                generation [MW] NUMERIC,
                cost [zł] NUMERIC)
            """
            cur.execute(g.format(table_name='gens'))
            for gen in gens:
                cur.execute("INSERT INTO gens VALUES(?, ?, ?)", (gen[0], gen[1], gen[2]))

            b = """
            CREATE TABLE {table_name} (
                node_from NUMERIC,
                node_to [MW] NUMERIC,
                flow [MW] NUMERIC)
            """
            cur.execute(b.format(table_name='branches'))
            for branch in branches:
                cur.execute("INSERT INTO branches VALUES(?, ?, ?)", (branch[0], branch[1], branch[2]))

            os.chdir('..')
            con.commit()
    return results_folder


# Pobieranie danych wybranej godziny z SQLite
def get_branches_data(request, hours):
    for i, folder_name in enumerate(hours):
        if 'hour_' + request == folder_name:
            os.chdir(folder_name)
            con = sqlite3.connect('data.db')
            cur = con.cursor()

            cur.execute("""SELECT * from branches""")
            branches_data = cur.fetchall()

            return branches_data
    print('Please enter correct hour')


# Tworzenie grafu
def create_graph(data_branches):
    modificated_data_for_graph = list(map(lambda x: (x[0], x[1], np.around(x[2], decimals=3)), data_branches))
    G = nx.DiGraph()
    G.add_weighted_edges_from(modificated_data_for_graph)
    labels = nx.get_edge_attributes(G, 'weight')
    pos = nx.spring_layout(G, k=0.7, weight='5', scale=5)
    nx.draw_networkx_nodes(G, pos, node_size=250, margins=0, alpha=0.3, cmap=plt.get_cmap('Greens'))
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=13, edge_color='red', min_source_margin=12,
                           min_target_margin=12, edgelist=G.edges())
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_labels(G, pos, font_size=10)
    plt.show()





folders = make_convert()
data = get_branches_data(input('Enter an hour You want to check:'), folders)
create_graph(data)
