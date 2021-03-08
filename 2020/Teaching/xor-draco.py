import socketserver
import base64
import string
import secrets
import re

dragon = '''
                         XOR
                 ___====-_  _-====___
           _--^^^#####//      \\\\#####^^^--_
        _-^##########// (    ) \\\\##########^-_
       -############//  |\^^/|  \\\\############-
     _/############//   (@::@)   \\\\############\_
    /#############((     \\\\//     ))#############\\
   -###############\\\\    (oo)    //###############-
  -#################\\\\  / VV \  //#################-
 -###################\\\\/      \//###################-
_#/|##########/\######(   /\   )######/\##########|\#_
|/ |#/\#/\#/\/  \#/\##\  |  |  /##/\#/  \/\#/\#/\#| \|
`  |/  V  V  `   V  \#\| |  | |/#/  V   '  V  V  \|  '
   `   `  `      `   / | |  | | \   '      '  '   '
                    (  | |  | |  )
                   __\ | |  | | /__
                  (vvv(VVV)(VVV)vvv)

'''

instrucciones = '''
    Hola, has entrado a la cueva de XOR, el dragon.
    El dragon habla lenguas infinitas y espera que seas amable y respondas en su lengua, de lo contrario sufriras su furia!

    Cada vez que vuelvas a la cueva el dragon hablara una lengua diferente. Puedes platicar con el, pero el solo respondera en su lengua.

    Tu reto es aprender su lengua, entonces podras pedirle su tesoro con la frase "Dame la llave ahora!"

    Pista. El dragon no habla base64, pero te entrega los mensajes en este formato para que puedan ser legibles.
    Pista2. El dragon solo recibe base64 es sus peticiones
    Pista3. La idea de este reto es aprender a usar pwntools, seguro encontraras formas muy sencillas de resolverlo.
'''
#NECESITAS ESTO###
with open("flag.txt") as f:
    flag = f.readline()

def gen_random_key(N):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(N))

def sxor(s1, s2):
    return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1, s2))

def bxor(b1,b2):
    return bytes([a^b for a, b in zip(b1,b2)])

def dragon_tongue(draco, llave):
    speech = ""
    piezas = re.findall(".{1,16}",str(draco,"utf-8"))
    for s in piezas:
        if len(s) is 16:
            speech += sxor(s,llave)
        else:
            speech += sxor(s,llave[:len(s)])
    return base64.b64encode(str.encode(speech))

def request_flag(flag_request, llave):
    speech = ''
    decoded = base64.b64decode(flag_request) 
    piezas = [decoded[i:i+16] for i in range(0,len(decoded),16)]
    for s in piezas:
        if len(s) is 16:
            speech += str(bxor(s,str.encode(llave)),"utf-8")
        else:
            speech += str(bxor(s,str.encode(llave[:len(s)])),"utf-8")
    if "Dame la llave ahora!" in speech:
        return True
    else:
        return False
    

class Dragon(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.send(str.encode(dragon))
        key = gen_random_key(16)
        print(key)
        opcion = 0
        while opcion != 4:
            try:
                self.request.send(b"\r\nSelecciona una opcion:\r\n")
                self.request.send(b"1. Leer instrucciones\r\n2. Hablar con el dragon\r\n3. Obtener el tesoro\r\n4. Escapar\r\n >>>> ")
                opcion = int(self.request.recv(1024).strip())
                if opcion == 1:
                    self.request.send(str.encode(instrucciones))
                    self.request.send(b"\r\n")
                if opcion == 2:
                    comando = 0
                    while comando != 2:
                        self.request.send(b"\r\n1. Hablar\r\n2. Escapar\r\n>>>> ")
                        comando = int(self.request.recv(1024).strip())
                        if comando is 1:
                            self.request.send(b"\r\nTu: ")
                            speech = self.request.recv(1024).strip()
                            self.request.send(b"\r\nDragon: ")
                            self.request.send(dragon_tongue(speech,key))
                        if comando is 2:
                            self.request.send(b"\r\nHasta pronto ")
                            break
                if opcion == 3:
                    self.request.send(b"\r\nSolo tienes una oportunidad. ")
                    self.request.send(b"\r\nComando: ")
                    speech = self.request.recv(1024).strip()
                    if request_flag(speech,key) is True:
                        self.request.send(str.encode(flag))
                    else:
                        self.request.send(b"Has sido calcinado por el dragon...")
                        break
                if opcion == 4:
                    self.request.send(b"\r\nGracias por participar!")
                    self.request.send(b"\r\n")

            except:
                self.request.send(b'\r\nOperacion no permitida...')
                self.request.send(b"\r\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 3102

    with socketserver.ThreadingTCPServer((HOST, PORT), Dragon) as server:
        server.allow_reuse_address = True
        server.serve_forever()