# this script is used to test scalability of our design
import requests
import time
import matplotlib.pyplot as plt
from threading import Thread

uri_get = "http://127.0.0.1:5000/"
uri_post = "http://127.0.0.1:5000/timetable/room"
test_1_results = []
test_2_results = []


def create_graph(y_values):
    x = 0
    for value in y_values:
        y = value[0]
        status_code = value[1]
        if status_code == 200:
            plt.plot(x, y, 'go')
        else:
            plt.plot(x, y, 'ro')
        x += 1
    plt.xlabel("Request")
    plt.ylabel("Response time")
    return plt


# sends a get request to API
def generate_get(num_request, test_1=False, test_2=False):
    for i in range(0, num_request):
        start_time = time.time()
        response = requests.get(uri_get)
        status_code = response.status_code
        end_time = time.time()
        time_taken = end_time - start_time
        result = (time_taken, status_code)
        if test_1:
            test_1_results.append(result)
        elif test_2:
            test_2_results.append(result)
    return "Test done"


# sends a post request to API
def generate_post(num_request, test_1=False, test_2=False):
    for i in range(0, num_request):
        start_time = time.time()
        response = requests.post(uri_post, data="T101")
        status_code = response.status_code
        end_time = time.time()
        time_taken = end_time - start_time
        result = (time_taken, status_code)
        if test_1:
            test_1_results.append(result)
        elif test_2:
            test_2_results.append(result)
    return "Test done"


# test to run 100 get request each from 10 clients
def test1():
    clients = []
    # create threads to run clients at same time
    # return the time and status code to the graph function
    for i in range(0, 10):
        clients.append(Thread(target=generate_get, kwargs=dict(num_request=100, test_1=True)))
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    average = sum([value[0] for value in test_1_results])/len(test_1_results)
    print(average)
    # call graph function
    graph = create_graph(test_1_results)
    return graph.show()


# test to run 1000 get request each from 100 clients
def test2():
    clients = []
    # create threads to run clients at same time
    # return the time and status code to the graph function
    for i in range(0, 100):
        clients.append(Thread(target=generate_get, kwargs=dict(num_request=100, test_2=True)))
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    average = sum([value[0] for value in test_2_results])/len(test_2_results)
    print(average)
    # call graph function
    graph = create_graph(test_2_results)
    return graph.show()


# test to run 100 post request each from 10 clients
def test3():
    clients = []
    # create threads to run clients at same time
    # return the time and status code to the graph function
    for i in range(0, 10):
        clients.append(Thread(target=generate_post, kwargs=dict(num_request=100, test_1=True)))
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    average = sum([value[0] for value in test_1_results]) / len(test_1_results)
    print(average)
    # call graph function
    graph = create_graph(test_1_results)
    return graph.show()


# test to run 1000 get request each from 100 clients
def test4():
    clients = []
    # create threads to run clients at same time
    # return the time and status code to the graph function
    for i in range(0, 100):
        clients.append(Thread(target=generate_post, kwargs=dict(num_request=100, test_2=True)))
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    average = sum([value[0] for value in test_2_results]) / len(test_2_results)
    print(average)
    # call graph function
    graph = create_graph(test_2_results)
    return graph.show()


def main():
    #test1()
    #test2()
    #test3()
    test4()



if __name__ == "__main__":
    main()
