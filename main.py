import psutil

for proc in psutil.process_iter(['pid', 'name', 'username']):
    if proc.info['name'] == 'mxx.exe':
        