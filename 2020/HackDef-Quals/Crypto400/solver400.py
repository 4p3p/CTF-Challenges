from pwn import *
import sys
import base64

conn = remote(sys.argv[1],int(sys.argv[2]))
conn.recvuntil("es: ")
token = conn.recvuntil(" para")[:-5]
conn.recvuntil("Eleccion: ")
conn.send("1\r\n")
iv = '\x41'*16
lbytes = list(bytes(iv,"utf-8"))
for i in range(0,0xFF):
        conn.recvuntil("token: ")
        conn.send(token)
        conn.recvuntil("inicializacion: ")
        lbytes[7] = i
        send = bytes(lbytes)
        try:
            conn.send(send)
        except:
            pass
        respuesta = conn.recv()
        if "idades" in str(respuesta,"utf-8"):
            print("ITERACION: %d" %i)
            print(respuesta)
        conn.send("S\r\n")
conn.close()
