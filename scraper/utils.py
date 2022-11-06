import pickle


def load_cookies(path):
    cookies = None
    
    with open(path, "rb") as file:
        cookies = pickle.load(file)
    
    assert cookies is not None, "Empty cookies"
    return cookies


def save_cookies(cookies, path):
    with open(path, "wb") as file:
        pickle.dump(cookies, file)