import pickle 

pickle_in = open("blocked_admin_dict.pickle","rb")
graph_dict = pickle.load(pickle_in)
print graph_dict