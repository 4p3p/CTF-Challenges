from flask import Flask,request,abort,redirect
import time
app = Flask(__name__)
from select import select
import sys
import random
import hashlib 

winner = '''
   ||====================================================================||
   ||//$\\\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//$\\\\||
   ||(0110)=================| HACKDEF CTF CHAMPION |===============(0110)||
   ||\\\\$//        ~         '------========--------'                \\\\$//||
   ||<< /        /$\\              // ____ \\\\                         \\ >>||
   ||>>|  12    //L\\\\            // ///..) \\\\         D34DB33F     12 |<<||
   ||<<|        \\\\ //           || <||  >\  ||                        |>>||
   ||>>|         \$/            ||  $$ --/  ||        One Billion     |<<||
||====================================================================||>||
||//$\\\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//$\\\\||<||
||(0110)=================| CONGRATULATIONS!!!!! |===============(0110)||>||
||\\\\$//        ~         '------========--------'                \\\\$//||\\||
||<< /        /$\\              // ____ \\\\                         \\ >>||)||
||>>|  12    //L\\\\            // ///..) \\\\            f99942     1 |<<||/||
||<<|        \\\\ //           || <||  >\\  ||                        |>>||=||
||>>|         \\$/            ||  $$ --/  ||        One Billion     |<<||
||<<|      1337H4X0R         *\\\\  |\\_/  //* series                 |>>||
||>>|  12                     *\\\\/___\\_//*   1337                  |<<||
||<<\\      Pwn3r!!!!   ______/U. FORTRESS\\________                 />>||
||//$\\                 ~|HACK DEFENDER 2019!!!!!!|~               /$\\\\||
||(0110)===================   ONE BILLION BTC  =================(0110)||
||\\\\$//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\\\$//||
||====================================================================||

FLAG: 1d3f34t3dth3f0rtr3ss

'''

class trueRandom(object):
    def __init__(self, p, a, c):
        self.p = p
        self.a = a
        self.c = c
        self.x = random.randint(0, p)

    def next(self):
        self.x = (self.a*self.x + self.c) % self.p
        return self.x

def gen(card):
    r = []
    q = card.split('-',4)
    p = int(q[1])*0x00D34DB33F
    a = int(q[2])*0x0BADC0FFEE
    c = int(q[3])
    o = trueRandom(p,a,c)
    for _ in range(8):
        r.append(o.next())
    return r

@app.route("/Challenge", methods=['POST'])
def Challenge():
    content = request.json
    if content['id-tarjeta'] and content['to'] and content['quantity']:
        if "-" not in content['id-tarjeta'] or len(content['id-tarjeta']) is not 19:
            return "La tarjeta debe tener la estructura: XXXX-XXXX-XXXX-XXXX\n"
        l = gen(content['id-tarjeta'])
        secret_number = int(str(l[-1:])[2:-1])
        with open(hashlib.md5(str.encode(content['id-tarjeta']+content['to']+content['quantity'])).hexdigest(),"w+") as t:
            t.write(str(secret_number))
            t.close()
        return "Challenge: {}\n".format(l[:-1])

@app.route("/Transaccion", methods=['POST'])
def Transaccion():
    content = request.json
    if content['id-tarjeta'] and content['challenge'] and content['to'] and content['quantity']:
        try:
            with open(hashlib.md5(str.encode(content['id-tarjeta']+content['to']+content['quantity'])).hexdigest()) as t:
                secret_number = t.read()
                t.close()
        except:
            return "Transaccion corrupta, genera nuevamente un challenge..."
        n = int(content['challenge'])
        if n == int(secret_number):
            if "1337-5868-4151-1749" in content['id-tarjeta']:
                return "\r\n"+content['quantity']+" transferidos a "+content['to']+"\n"+"{}".format(winner)
            else:
                return "\r\n"+content['quantity']+" transferidos a "+content['to']+"\n"

    return "{\"Error\":\"Transaccion Fallida o datos corruptos\"}"

@app.route("/flag", methods=['POST','GET'])
def Flag():
    return redirect("https://bit.ly/IqT6zt", code=302)

if __name__ == "__main__":
    app.run(host='0.0.0.0')