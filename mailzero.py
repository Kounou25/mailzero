from flask import Flask,request,jsonify,session
from email import message_from_bytes
from email.header import decode_header
import imapclient

app = Flask(__name__)
user_connexions = {}
filtered_emails = {}
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
    

#fonction qui se charge de compter et retourner le nombre de mail trouver en fonction des filtres appliques
def mail_counter(email):
    founded_mail = filtered_emails.get(email)
    return len(founded_mail)


    

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


#endpoint pour recevoir les filtres
@app.route('/mailzero/filters',methods=['POST'])
def filters():
    data = request.json
    email = data.get('email')
    wolf = user_connexions.get(email)
    folder = data.get('folder')
    filters = data.get('filter')
    if not wolf :
        return jsonify({"error":"Utilisateur non connecté ou introuvable !"}),404
    else:
        try:
            wolf.select_folder(folder)
            found_emails = wolf.search(filters)
            # Stocker les résultats pour cet utilisateur
            filtered_emails[email] = found_emails
            return jsonify({"message": "Emails filtrés récupérés avec succès !"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

@app.route('/mailzero/count_mails',methods=['GET'])
def count_mails():
    email = request.args.get('email')
    wolf = user_connexions.get(email)

    if not wolf:
        return jsonify({"error":"Utilisateur non connecter ou introuvable !"}),404
    else:
        try:
            counted_mails = mail_counter(email)
            if not counted_mails :
                return jsonify({"error":"Erreur lors de la recuperation !"}),401
            else:
                return jsonify({"message":f"{counted_mails} trouvé !"}),200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/mailzero/display_mails',methods=['GET'])
def display_mails():
    email = request.args.get('email')
    wolf = user_connexions.get(email)
    founded_mails = filtered_emails.get(email)
    emails_list = []

    if not wolf :
        return jsonify({"error":"Utilisateur non connecté ou introuvable !"}),404
    else:
        try:
            

            brut_email_data = wolf.fetch(founded_mails, ['BODY.PEEK[]'])
            for email_id in founded_mails:
                email_data = brut_email_data[email_id][b'BODY[]']
                processed_email_data = message_from_bytes(email_data)

                #maintenant je recupere les données souhaité des emails exemple: objets,contenu etc...
                subject_header = processed_email_data.get("subject", "Sans sujet")
                email_subject = decode_header(subject_header)[0][0] if subject_header else "Sans sujet"
                if isinstance(email_subject, bytes):
                    email_subject = email_subject.decode()
                receive_date = processed_email_data["date"]
                sender = processed_email_data["from"]
                receiver = processed_email_data["To"]

                emails_list.append({
                    "objet":email_subject,
                    "date reception":receive_date,
                    "emetteur":sender,
                    "Destinataire":receiver,
                })

            return jsonify({"emails":emails_list}),200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True,port=9000)