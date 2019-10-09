import threading
import time
from werkzeug.local import Local


# class A:
#     a = 1


my_obj = Local()
my_obj.a = 1


def work():
    my_obj.a = 2
    print('new thread ' + str(my_obj.a))


run = threading.Thread(target=work, name='wyq')
run.start()
time.sleep(1)
print('main thread ' + str(my_obj.a))
