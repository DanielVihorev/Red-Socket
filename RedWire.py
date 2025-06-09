import os
import pwd
import socket
import subprocess
import json

HOST = '127.0.0.1'
PORT = 5000

def search_files_by_user(username):
    uid = pwd.getpwnam(username).pw_uid
    matches = []
    for root, dirs, files in os.walk('/'):
        for name in files:
            try:
                path = os.path.join(root, name)
                if os.stat(path).st_uid == uid:
                    matches.append(path)
            except Exception:
                continue
    return matches

def handle_client(conn):
    while True:
        data = conn.recv(4096)
        if not data:
            break
        try:
            req = json.loads(data.decode())
            cmd = req.get('cmd')
            if cmd == "exec":
                output = subprocess.getoutput(req['command'])
                conn.sendall(output.encode())
            elif cmd == "search_files":
                files = search_files_by_user(req['username'])
                conn.sendall(json.dumps(files).encode())
            elif cmd == "get_file":
                with open(req['filepath'], 'rb') as f:
                    conn.sendall(f.read())
            else:
                conn.sendall(b"Invalid command\n")
        except Exception as e:
            conn.sendall(f"ERROR: {e}\n".encode())

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                handle_client(conn)

if __name__ == "__main__":
    main()