import pickle


# Store file id against file name locally

# Load data with pickle
def load_data():
    try:
        with open('file_data.pickle', 'rb') as handle:
            return pickle.load(handle)
    except (FileNotFoundError, EOFError):
        return {}


# Store data with pickle
def store_data(data):
    with open('file_data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


# Function to add new item
def add_item(file_id, file_name):
    data = load_data()
    data[file_id] = file_name
    store_data(data)


# Function to query file_name by file_id
def get_file_name(file_id):
    data = load_data()
    return data.get(file_id, "not found")
