import sys
import socket
import threading
from queue import Queue
import argparse
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from time import sleep

queue = Queue()


def sock_connect(target, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    output = sock.connect_ex((target, port))
    sock.close()
    return output


def main():
    parser = argparse.ArgumentParser('Smart PortScanner')
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="The target IP address")
    parser.add_argument("-p", "--port", type=str, help="<port-range>")
    parser.add_argument("-t", "--thread", type=int, help="threads to run")
    args = parser.parse_args()

    if(len(sys.argv) < 2):
        parser.print_help()
        sys.exit(0)

    target = args.address
    
    if target is not None:
        portNumbers = args.port.split('-')
        threads = args.thread
        for Ports in range(int(portNumbers[0]), int(portNumbers[1])):
            queue.put(Ports)

    thread_runner(threads, target)


def scanner(target):
    while not queue.empty():
        port = queue.get()
        if sock_connect(target, port) == 0:
            service = socket.getservbyport(port)
            print("[+] Port {}/tcp is open".format(port))
            print("[+] Banner : {}\n".format(service))
            if port == 80 or port ==443:
                takeshot(target, port)

        else:
            print("[+] Port {}/tcp is closed".format(port))


def takeshot(target, port):
    options = Options()
    options.headless = True
    fire = webdriver.Firefox(options=options)
    try:
        fire.get('https://'+target)
    except:
        fire.get("http://"+ target)

    sleep(1)
    fire.get_screenshot_as_file("{}.png".format(target + str(port)))
    fire.quit()
    fire.quit()


def thread_runner(threads, target):

    thread_list = []
    try:
        for t in range(threads):
            thread = threading.Thread(target=scanner, args=(target,))
            thread_list.append(thread)

        for thread in thread_list:
            thread.start()
    except BaseException:
        pass


if __name__ == "__main__":
    main()
