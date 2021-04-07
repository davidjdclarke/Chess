import threading


def calculate(number):
    if number == 1:
        return number
    else:
        return number * calculate(number-1)

if __name__ == "__main__":
    thread = threading.Thread(target=calculate, args=(100000,))
    thread.start()
    value = thread.join()
    print(value)