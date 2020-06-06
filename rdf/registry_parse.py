import rdflib
import pickle

g = rdflib.Graph()
result = g.parse("registry.rdf")

with open('registry.pickle', 'wb') as f:
    pickle.dump(g, f, pickle.HIGHEST_PROTOCOL)
