import psutil

_last_cpu_check = 0
_cached_cpu = 0

def get_cpu_usage():
    global _last_cpu_check, _cached_cpu
    import time
    now = time.time()
    
    if now - _last_cpu_check > 5:
        _cached_cpu = psutil.cpu_percent(interval=None)
        _last_cpu_check = now
    return _cached_cpu

def adjust_limit(base):
    cpu = get_cpu_usage()
    
    if cpu > 80:
        return int(base * 0.5)
    elif cpu > 50:
        return int(base * 0.8)
    
    return base