import psutil
import datetime
import platform
import time

class SystemMonitor:
    def __init__(self):
        self.system_start_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.processes = []
        self.disk_partitions = []
        
        # Data storage variables
        self.cpu_data = {}
        self.memory_data = {}
        self.temperature_data = {}
        self.network_data = {}
        self.system_data = {}
        self.disk_data = []
        self.process_data = []
        
    def get_hardware_temperatures(self):
        """Get hardware temperatures - Linux only"""
        self.temperature_data = {}
        if self.is_linux:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        self.temperature_data[name] = []
                        for entry in entries:
                            self.temperature_data[name].append({
                                'label': entry.label or 'N/A',
                                'current': entry.current
                            })
                else:
                    self.temperature_data['status'] = "No temperature sensors found"
            except AttributeError:
                self.temperature_data['status'] = "Temperature monitoring not available"
        else:
            self.temperature_data['status'] = "Hardware temperatures not available on Windows"
    
    def get_cpu_info(self):
        """Get CPU usage and core count"""
        cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
        core_count = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        
        self.cpu_data = {
            'usage_percent': cpu_usage,
            'physical_cores': core_count,
            'logical_cores': logical_cores
        }
        
        return cpu_usage, core_count
    
    def get_memory_info(self):
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.memory_data = {
            'usage_percent': memory.percent,
            'available_gb': memory.available // (1024**3),
            'total_gb': memory.total // (1024**3),
            'swap_usage_percent': swap.percent if swap.total > 0 else 0,
            'has_swap': swap.total > 0
        }
        
        return memory.percent
    
    def refresh_processes(self):
        """Refresh and display top processes by memory usage"""
        try:
            self.processes = sorted(
                psutil.process_iter(['pid', 'name', 'memory_percent']), 
                key=lambda p: p.info['memory_percent'] if p.info['memory_percent'] else 0, 
                reverse=True
            )
            
            self.process_data = []
            for proc in self.processes[:5]:
                if proc.info['memory_percent'] is not None:
                    self.process_data.append({
                        'name': proc.info['name'],
                        'memory_percent': proc.info['memory_percent']
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            self.process_data = [{'error': "Error accessing some process information"}]
    
    def clear_processes(self):
        """Clear the processes list"""
        self.processes.clear()
        print("Process list cleared")
    
    def refresh_disk_info(self):
        """Refresh and display disk usage information"""
        try:
            self.disk_partitions = psutil.disk_partitions()
            self.disk_data = []
            
            for partition in self.disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total // (1024**3)
                    used_gb = usage.used // (1024**3)
                    free_gb = usage.free // (1024**3)
                    
                    # Windows vs Linux path formatting
                    device_name = partition.device if self.is_windows else partition.mountpoint
                    
                    self.disk_data.append({
                        'device': device_name,
                        'usage_percent': usage.percent,
                        'total_gb': total_gb,
                        'used_gb': used_gb,
                        'free_gb': free_gb,
                        'filesystem': partition.fstype
                    })
                    
                except PermissionError:
                    self.disk_data.append({
                        'device': partition.device,
                        'error': "Permission denied"
                    })
        except Exception as e:
            self.disk_data = [{'error': f"Error getting disk information: {e}"}]
    
    def clear_disk_info(self):
        """Clear the disk partitions list"""
        self.disk_partitions.clear()
        print("Disk partitions list cleared")
    
    def get_network_info(self):
        """Get network interface information"""
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        self.network_data = {}
        for interface_name, addresses in interfaces.items():
            if interface_name in stats:
                stat = stats[interface_name]
                self.network_data[interface_name] = {
                    'status': 'Up' if stat.isup else 'Down',
                    'addresses': []
                }
                for addr in addresses:
                    if addr.family == psutil.AF_LINK:  # MAC address
                        self.network_data[interface_name]['addresses'].append({
                            'type': 'MAC',
                            'address': addr.address
                        })
                    elif addr.family == 2:  # IPv4
                        self.network_data[interface_name]['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address
                        })
    
    def display_system_info(self):
        """Display one-time system information"""
        self.system_data = {
            'start_time': self.system_start_time,
            'os': f"{platform.system()} {platform.release()}",
            'architecture': platform.machine(),
            'processor': platform.processor()
        }
    
    def print_all_data(self):
        """Print all collected system information"""
        print("=" * 50)
        print("LanWatch System Monitor")
        print("=" * 50)
        
        # System Information
        if self.system_data:
            print(f"System Start Time: {self.system_data['start_time']}")
            print(f"Operating System: {self.system_data['os']}")
            print(f"Architecture: {self.system_data['architecture']}")
            print(f"Processor: {self.system_data['processor']}")
        
        # CPU Information
        if self.cpu_data:
            print(f"\nCPU Usage: {self.cpu_data['usage_percent']}%")
            print(f"Physical Cores: {self.cpu_data['physical_cores']}")
            print(f"Logical Cores: {self.cpu_data['logical_cores']}")
        
        # Memory Information
        if self.memory_data:
            print(f"\nMemory Usage: {self.memory_data['usage_percent']}%")
            print(f"Available Memory: {self.memory_data['available_gb']} GB")
            print(f"Total Memory: {self.memory_data['total_gb']} GB")
            if self.memory_data['has_swap']:
                print(f"Swap Usage: {self.memory_data['swap_usage_percent']}%")
        
        # Process Information
        if self.process_data:
            print("\nTop 5 processes by memory usage:")
            for proc in self.process_data:
                if 'error' in proc:
                    print(f"  {proc['error']}")
                else:
                    print(f"  {proc['name']}: {proc['memory_percent']:.2f}%")
        
        # Temperature Information
        if self.temperature_data:
            if 'status' in self.temperature_data:
                print(f"\n{self.temperature_data['status']}")
            else:
                print("\nHardware Temperatures:")
                for name, entries in self.temperature_data.items():
                    for entry in entries:
                        print(f"  {name} {entry['label']}: {entry['current']}°C")
        
        # Network Information
        if self.network_data:
            print("\nNetwork Interfaces:")
            for interface_name, data in self.network_data.items():
                print(f"  {interface_name}: {data['status']}")
                for addr in data['addresses']:
                    print(f"    {addr['type']}: {addr['address']}")
        
        # Disk Information
        if self.disk_data:
            print("\nDisk Usage:")
            for disk in self.disk_data:
                if 'error' in disk:
                    print(f"  {disk.get('device', 'Unknown')}: {disk['error']}")
                else:
                    print(f"  {disk['device']}: {disk['usage_percent']:.1f}% used")
                    print(f"    Total: {disk['total_gb']} GB, Used: {disk['used_gb']} GB, Free: {disk['free_gb']} GB")
                    print(f"    Filesystem: {disk['filesystem']}")
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        # One-time checks
        self.display_system_info()
        
        # Refresh often
        self.get_cpu_info()
        self.get_memory_info()
        self.refresh_processes()
        
        # Hardware temperatures (Linux only)
        self.get_hardware_temperatures()
        
        # Network information
        self.get_network_info()
        
        # Refresh periodically
        self.refresh_disk_info()
        
        # Print all collected data
        self.print_all_data()

def main():
    monitor = SystemMonitor()
    monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()