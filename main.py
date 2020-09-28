from multiprocessing import Process, Pipe
from datetime import datetime


def local_time(counter):
    return ' (Counter={}, LOCAL_TIME={})'.format(counter, datetime.now())


def calc_recv_timestamp(recv_time_stamp, counter):
    for id in range(len(counter)):
        counter[id] = max(recv_time_stamp[id], counter[id])
    return counter


def event(pid, counter):
    counter[pid] += 1
    print('Something happened in {} !'.format(pid) + local_time(counter))
    return counter


def send_message(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(('Empty shell', counter))
    print('Message sent from ' + str(pid) + local_time(counter))
    return counter


def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter)
    counter[pid] += 1
    print('Message received at ' + str(pid) + local_time(counter))
    return counter


def process_a(pipe_ab):
    pid = 0
    counter = [0, 0, 0]
    counter = send_message(pipe_ab, pid, counter)
    counter = send_message(pipe_ab, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_ab, pid, counter)
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_ab, pid, counter)
    print("Process A final counter: {}".format(counter))


def process_b(pipe_ba, pipe_bc):
    pid = 1
    counter = [0, 0, 0]
    counter = recv_message(pipe_ba, pid, counter)
    counter = recv_message(pipe_ba, pid, counter)
    counter = send_message(pipe_ba, pid, counter)
    counter = recv_message(pipe_bc, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe_ba, pid, counter)
    counter = send_message(pipe_bc, pid, counter)
    counter = send_message(pipe_bc, pid, counter)
    print("Process B final counter: {}".format(counter))


def process_c(pipe_cb):
    pid = 2
    counter = [0, 0, 0]
    counter = send_message(pipe_cb, pid, counter)
    counter = recv_message(pipe_cb, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_cb, pid, counter)
    print("Process C final counter: {}".format(counter))


if __name__ == '__main__':
    ab, ba = Pipe()
    bc, cb = Pipe()

    process_A = Process(target=process_a, args=(ab,))
    process_B = Process(target=process_b, args=(ba, bc))
    process_C = Process(target=process_c, args=(cb,))

    process_A.start()
    process_B.start()
    process_C.start()

    process_A.join()
    process_B.join()
    process_C.join()
