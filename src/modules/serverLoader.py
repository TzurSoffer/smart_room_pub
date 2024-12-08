import multiprocessing
import importlib

def run(target, args=()):
    module = importlib.import_module(target)
    try:
        multiprocessing.Process(target=module.run, args=args).start()
    except Exception as e:
        print(f"{target} has failed to start with error: {e}.")



if __name__ == '__main__':
    run("clapDetectorRun", args=(2000, 3000))
    print("Finished loading all modules for the smart room")
    multiprocessing.freeze_support()

# run(mqttCamera.run)
# run(target=audioSender.run, args=(20, "USB Audio Device"))
# run(target=alarm.run)
# run(target=cameraBufferHandler.run)
# run(target=movementDetection.run, args=(5, 4))
# run(target=clapDetectorRun.run)
# run(target=autoLightsTurnOff.run)