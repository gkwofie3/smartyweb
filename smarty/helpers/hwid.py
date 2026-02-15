import subprocess
import hashlib

def get_hwid():
    """
    Generates a unique HWID based on machine identifiers (Windows).
    Uses BIOS and CPU serial numbers.
    """
    try:
        # Get BIOS Serial
        bios_serial = subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip()
        # Get CPU Serial
        cpu_id = subprocess.check_output('wmic cpu get processorid').decode().split('\n')[1].strip()
        
        raw_id = f"{bios_serial}:{cpu_id}"
        return hashlib.sha256(raw_id.encode()).hexdigest()
    except Exception:
        # Fallback for non-windows or errors
        return "GENERIC-HWID-001"
