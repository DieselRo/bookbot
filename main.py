from stats import get_num_words
from stats import get_num_chars_dict
from stats import sort_dict
import sys


def get_book_text(input):
    """
    Reads the content of a text file and returns it as a string.
    
    Args:
        input (str): The path to the text file.
        
    Returns:
        str: The content of the text file.
    """
    with open(input, 'r', encoding='utf-8') as file:
        return file.read()



def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_book>")
        sys.exit(1)
    else:
        print(f"Using provided file path: {sys.argv[1]}")
        
    
        book_text = get_book_text(sys.argv[1])
        num_words = get_num_words(book_text)
        meatoftheproject = get_num_chars_dict(book_text)
        meatoftheproject = sort_dict(meatoftheproject)
        print("============ BOOKBOT ============")
        print(f"Analyzing book found at {sys.argv[1]}...")
        print("------------ WORD COUNT ------------")
        print(f"Found {num_words} total words")
        print("--------- CHARACTER COUNT -----------")
        for item in meatoftheproject:

            char = item["char"]
            count = item["num"]
            if char.isalpha():
             print(f"{char}: {count}")
        print("============= END =============")
    
    


if __name__ == "__main__":
    main()