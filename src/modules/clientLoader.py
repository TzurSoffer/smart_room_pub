import multiprocessing
import importlib

def run(target, args=()):
    module = importlib.import_module(target)
    try:
        multiprocessing.Process(target=module.run, args=args).start()
    except:
        print(f"{target} has failed to start.")
run(target="mqttCamera", args=(5,))
run(target="audioSender", args=(30, "USB Audio Device"))
run(target="movementDetection", args=(1/2, 4))
run(target="cameraBufferHandler", args=())
print("Finished loading all modules for the smart room")
