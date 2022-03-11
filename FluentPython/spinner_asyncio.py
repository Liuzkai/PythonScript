import asyncio
import itertools
import threading
import time
from turtle import down

def spin2(msg, done):
    for chars in itertools.cycle('|/-\\'):
        status = chars + ' ' + msg
        print(status, flush=True, end='\r')
        if done.wait(0.1) :
            break



def slow_function2(delay):
    time.sleep(delay)
    return 32


def supervisor2():
    done = threading.Event()
    spinner = threading.Thread(target=spin2, args=('thinking...' , done))
    spinner.start()
    result = slow_function2(3.0)
    done.set()
    spinner.join()
    return result


async def spin(msg):
    for chars in itertools.cycle('|/-\\'):
        status = chars + ' ' + msg
        print(status, flush=True, end='\r')
        try:
            await asyncio.sleep(.1)
        except asyncio.CancelledError:
            break
    print(' ' * len(status))


async def slow_function(delay):
    await asyncio.sleep(delay)
    return 42


async def supervisor():
    spinner = asyncio.create_task(spin('thinking...'))
    print('spinner : ' , spinner)
    result = await slow_function(3)
    spinner.cancel()
    return result


def main():
    t0 = time.time()
    result = asyncio.run(supervisor())
    print(result)
    t1 = time.time() - t0
    print('asyncio time count : {:.2f}'.format(t1))
    
    t0 = time.time()
    result = supervisor2()
    print(result)
    t1 = time.time() - t0
    print('threading time count : {:.2f}'.format(t1))
    


if __name__ == '__main__':
    main()