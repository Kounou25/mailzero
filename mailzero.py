from flask import Flask,request,jsonify
from email import message_from_bytes
import imapclient

app = Flask(__name__)
user_connexions = {}

def mail_connection(email,password):
    try:
        wolf = imapclient.IMAPClient('imap.gmail.com',ssl=True)
        wolf.login(email,password)
        print('connexion etablie avec succes !')
        return wolf
    except Exception as e:
        print(f"une erreur s'est produite lors de la connexion au compte {email}: {e}")
        return 1
    

#endpoint de connexion au compte gmail
@app.route('/mailzero/connect', methods=['POST'])
def connexion():
    #on recupere et extrait l'adresse email et le password envoyer dans la requete
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error":'Email et Mot de passe requis !'}),400
    
    #si tout est bon, on etablie la connexion au compte gmail

    wolf = mail_connection(email,password)
    if wolf !=1:
        user_connexions[email]= wolf
        return jsonify({"message":f'connexion etablie avec succes pour: {email}'}),200
    else:
        return jsonify({"error": 'erreur de la connexion !'}),401
        





if __name__ == '__main__':
    app.run(debug=True,port=9000)