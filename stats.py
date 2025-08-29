def get_num_words(string):
    """
    Counts the number of words in a given string.
    
    Args:
        string (str): The input string.
        
    Returns:
        int: The number of words in the string.
    """
    words = string.split()
    return len(words)

def get_num_chars_dict(string):
    """
    Counts the occurrences of each character in a given string.
    
    Args:
        string (str): The input string.
        
    Returns:
        dict: A dictionary with characters as keys and their counts as values.
    """
    char_count = {}
    for char in string:
        char = char.lower()
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1
    return char_count

def sort_on(items):
        return items["num"]

def sort_dict(dict):
        dict_list = []


        #{"b": 4868}
        #{"char": "b", "num": 4868}
        for key in dict:
            char_dict = {}
            count = dict[key]
            char_dict["char"] = key
            char_dict["num"] = count
            dict_list.append(char_dict)
        dict_list = sorted(dict_list, key=sort_on, reverse=True)
        return dict_list
        
def report_list(dict_list):
    for item in dict_list:
        char = item["char"]
        num = item["num"]
        print(f"Character '{char}' found {num} times")       

    
            
        
        