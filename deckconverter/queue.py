import queue

flipperQueue = None

def initQueue():
    global flipperQueue
    if flipperQueue == None:
        flipperQueue = queue.Queue()

    return flipperQueue

def sendMessage(message):
    global flipperQueue
    if flipperQueue:
        flipperQueue.put(message)
