from flask import Flask,request,abort,redirect
import time
app = Flask(__name__)
from Crypto.Cipher import AES
from select import select
import sys
import base64
from secret import flag, key, padc

@app.route("/Hack", methods=['POST'])
def Hack():
    content = request.json
    equipo = content['alumno']
    assert (len(flag) == 32) and (len(key) == 32)
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = equipo + flag
    l = len(plaintext)
    padl = (l // 32 + 1)*32 if l % 32 != 0 else 0
    plaintext = plaintext.ljust(padl, padc)
    ciphertext = (cipher.encrypt(bytes(plaintext,"utf-8"))).hex()
    return "Ticket: {}".format(base64.urlsafe_b64encode(bytes.fromhex(ciphertext)).decode('utf-8'))

@app.route("/Defender", methods=['POST'])
def Defender():
    content = request.json
    ticket = content['ticket']
    cipher = AES.new(key, AES.MODE_ECB)
    try:
        decoded = base64.urlsafe_b64decode(ticket)
        plain = cipher.decrypt(decoded)
        plaintext = plain.decode('utf-8')[0:(plain.decode('utf-8')).find(flag)]
    except:
        return "ERROR!!!!\n Warning: URL SAFETY ENABLED!\n"
    return "Hola {}, tu ticket es valido! Ha sido concatenado con la bandera!!!".format(plaintext)

@app.route("/Flag", methods=['POST','GET'])
def Flag():
    return redirect("https://bit.ly/IqT6zt", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
