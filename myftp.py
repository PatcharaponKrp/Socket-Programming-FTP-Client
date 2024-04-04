import socket
import os

SERVER_ADDRESS = "ftp.example.com"  
SERVER_PORT = 21  

transfer_mode = "ascii"
connected = False

def connect():
  global connected
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_ADDRESS, SERVER_PORT))
    welcome_message = sock.recv(1024).decode()
    print(welcome_message)
    connected = True
    return sock
  except Exception as e:
    print(f"Failed to connect: {e}")
    connected = False
    return None

def disconnect(sock):
  global connected
  try:
    sock.sendall(b"QUIT\r\n")
    response = sock.recv(1024).decode()
    print(response)
    sock.close()
    connected = False
  except Exception as e:
    print(f"Failed to disconnect: {e}")

def send_command(sock, command):
  sock.sendall(command.encode() + b"\r\n")
  response = sock.recv(1024).decode()
  return response

def download_file(sock, remote_filename, local_filename):
  send_command(sock, f"RETR {remote_filename}")
  response = sock.recv(1024).decode()
  if response.startswith("226"):  # การถ่ายโอนข้อมูลเริ่มต้น
    with open(local_filename, "wb") as f:
      while True:
        data = sock.recv(1024)
        if not data:
          break
        if transfer_mode == "binary":
          f.write(data)
        else:
          f.write(data.decode(transfer_mode))
  else:
    print(f"Error downloading file: {response}")

def upload_file(sock, remote_filename, local_filename):
  with open(local_filename, "rb") as f:
    send_command(sock, f"STOR {remote_filename}")
    response = sock.recv(1024).decode()
    if response.startswith("150"):  
      while True:
        data = f.read(1024)
        if not data:
          break
        if transfer_mode == "binary":
          sock.sendall(data)
        else:
          sock.sendall(data.encode(transfer_mode))
    else:
        print(f"Error uploading file: {response}")

def process_command(command):
  global transfer_mode

  if not command:
    return

  if command.startswith("ascii"):
    transfer_mode = "ascii"
    print(f"Transfer mode set to ASCII")
  elif command.startswith("binary"):
    transfer_mode = "binary"
    print(f"Transfer mode set to Binary")
  elif command.startswith("bye"):
    if connected:
      disconnect(sock)
  elif command.startswith("cd"):
    if connected:
      path = command
