import psutil, datetime

# hardware temperatures are NOT available on Windows, but are on Linux

# one time checks

systemStartTime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

# refresh often

cpuUsagePercentage = psutil.cpu_percent(interval=1, percpu=False)
coreCount = psutil.cpu_count(logical=False)
memoryUsage = psutil.virtual_memory().percent

# fix this to be tied to a variable and cleared properly
processes = sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), 
                  key=lambda p: p.info['memory_percent'], 
                  reverse=True)
print("Top 5 processes by memory usage:")
for proc in processes[:5]:
    print(f"  {proc.info['name']}: {proc.info['memory_percent']:.2f}%")

# refresh every once in awhile

# fix this to be tied to a variable
for partition in psutil.disk_partitions():
    usage = psutil.disk_usage(partition.mountpoint)
    print(f"Disk {partition.device}: {usage.percent}% used of {usage.total // (1024**3)} GB")

