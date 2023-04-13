# utils.py
def print_seperator_tilda():
    print("~" * 80)

def print_seperator_star():
    print("*" * 80)

def print_seperator_plus():
    print("+" * 80)

def print_table_header_seperator(length):
    print("_" * length)


#def print_table_header(length,message):
#    print (" ")
#    print_table_header_seperator(length)
#    print(f"\033[1m{message}\033[0m")
#    print_table_header_seperator(length)

def print_error(message):
    print (" ")
    print_seperator_plus ()
    print(f"Error : {message}")
    print_seperator_plus ()
    print (" ")

def print_title(message):
    print (" ")
    print (" ")
    print_seperator_tilda ()
    print(f"\033[1m{message}\033[0m")
    print_seperator_tilda ()

def print_info(message):
    print (" ")
    print_seperator_star ()
    print(f"Info  : {message}")
    print_seperator_star ()