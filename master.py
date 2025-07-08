import subprocess

print("running scanner")
subprocess.run(["python3", "scanner.py"])
print('finished running scanner')

print("running script")
subprocess.run(["python3", "script.py"])
print("finished running script")

