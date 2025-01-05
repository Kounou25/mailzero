from flask import Flask,request,jsonify,session
from email import message_from_bytes
import imapclient

app = Flask(__name__)
user_connexions = {}
app.secret_key="kounougilbert288@predator2024"


#----------------------- logiques du programme -----------------------------
#foonction de connexion au compte gmail
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
        

#endpoint pour verifier le status de la connexion
@app.route('/mailzero/status',methods=['GET'])
def connexion_status():
    #on recupere d'abord l'email rechercher depuis la requete
    conn_email = request.args.get('email')

    if conn_email in user_connexions:
        return jsonify({"status":f"{conn_email} est connecté !"}),200
    else:
        return jsonify({"status":f"{conn_email} n'est pas connecté !"}),404
    

#endpoint pour la deconnexion au compte gmail
@app.route('/mailzero/disconnect',methods=['POST'])
def disconnect():
    #on recupere d'abord l'email depuis la requete
    data = request.json
    kill_email = data.get('email')
    if not kill_email or not kill_email in user_connexions:
        return jsonify({"error":"aucune connexion trouver pour cet email !"}),404
    else:
        #deconnecter et supprimer l'email contenu dans le dictionnaire
        kill_connexion = user_connexions.pop(kill_email)
        kill_connexion.logout()
        return jsonify({"message":"deconnexion effectuer avec succes !"}),200

#----------------------- endpoints pour d'autres fonctionnalites autres que lq connexion

@app.route('/mailzero/folders',methods=['GET'])
#fonction pour lister les dossiers du compte gmail
def folders_list():
    email = request.args.get('email')
    wolf = user_connexions.get(email)

    if not wolf:
        return jsonify({"error": "Utilisateur non connecté ou introuvable"}), 404

    try:
        folders = wolf.list_folders()
        folder_names = [folder[-1] for folder in folders]
        return jsonify({"folders": folder_names}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    




if __name__ == '__main__':
    app.run(debug=True,port=9000)