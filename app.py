from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

import pymysql.cursors

# (interface de serveur web python)
# comportements et méthodes d'un serveur web
app = Flask(__name__)    # instance de classe Flask (en paramètre le nom du module)
app.secret_key = 'secreeet'

def get_db():
    #mysql --user=jgenitri --password=1511 --host=serveurmysql --database=BDD_jgenitri
    if 'db' not in g:
        g.db = pymysql.connect(
            host="localhost",                 # à modifier
            user="jgenitri",                     # à modifier
            password="1511",                # à modifier
            database="BDD_jgenitri",        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def setup_database():
    db = get_db()
    try:
        with open('script.sql', 'r') as f:
            sql_script = f.read()
        with db.cursor() as cursor:
            # Exécutez le script SQL ligne par ligne
            for command in sql_script.split(';'):
                command = command.strip()
                if command:  # Assurez-vous que la commande n'est pas vide
                    cursor.execute(command)
        db.commit()  # Sauvegarder les changements
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_layout():
    return render_template('layout.html')

@app.route('/ticket/show')
def show_ticket():
    mycursor = get_db().cursor()
    sql = '''
    SELECT ticket_incident.id_ticket AS id,
    ticket_incident.description_incident AS description,
    ticket_incident.date_incident AS date,
    ticket_incident.statut_incident AS statut,
    ticket_incident.parcelle_concernee AS parcelle,
    parcelle.adresse AS adresse FROM ticket_incident LEFT JOIN parcelle ON parcelle.id_parcelle = ticket_incident.parcelle_concernee;
    '''
    mycursor.execute(sql)
    ticket_incident = mycursor.fetchall()

    return render_template('tickets/show_ticket.html', ticket_incident=ticket_incident)

@app.route('/ticket/add', methods=['GET'])
def add_ticket():
    mycursor = get_db().cursor()
    sql='''
    SELECT ticket_incident.id_ticket AS id FROM ticket_incident;
    '''
    mycursor.execute(sql)
    ticket = mycursor.fetchall()
    sql = '''
    SELECT parcelle.id_parcelle AS id, parcelle.adresse AS adresse FROM parcelle;
    '''
    mycursor.execute(sql)
    parcelle = mycursor.fetchall()
    return render_template('tickets/add_ticket.html', ticket=ticket, parcelle=parcelle)

@app.route('/ticket/add', methods=['POST'])
def valid_add_ticket():
    mycursor = get_db().cursor()

    description_ticket = request.form.get('description_ticket', '')
    date = request.form.get('date', '')
    statut_incident = request.form.get('statut', '')
    parcelle_concernee = request.form.get('parcelle', '')
    tuple_insert = (description_ticket, date, statut_incident, parcelle_concernee)
    sql = '''
    INSERT INTO ticket_incident(description_incident, date_incident, statut_incident, parcelle_concernee)
    VALUES (%s, %s, %s, %s);
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    message = u'Nouveau ticket , description : '+description_ticket + ' | date : ' + date + \
                ' | statut : ' + statut_incident+ '| parcelle_concernee : '+ parcelle_concernee
    flash(message, 'alert-success')

    return redirect('/ticket/show')

@app.route('/ticket/delete', methods=['GET'])
def delete_ticket():
    mycursor = get_db().cursor()
    id_ticket = request.args.get('id', '')
    tuple_delete = (id_ticket)
    sql = '''
    DELETE FROM ticket_incident WHERE id_ticket = %s;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    message=u'Un ticket supprimé ! id : ' + id_ticket
    flash(message, 'alert-warning')
    return redirect('/ticket/show')

@app.route('/ticket/edit', methods=['GET'])
def edit_ticket():
    mycursor = get_db().cursor()

    id = request.args.get('id', '')
    sql = '''
        SELECT ticket_incident.id_ticket AS id,
        ticket_incident.description_incident AS description,
        ticket_incident.date_incident AS date,
        ticket_incident.statut_incident AS statut,
        ticket_incident.parcelle_concernee AS parcelle FROM ticket_incident WHERE ticket_incident.id_ticket=%s;
        '''
    mycursor.execute(sql, (id))

    ticket = mycursor.fetchone()
    sql = '''
        SELECT parcelle.id_parcelle AS id, parcelle.adresse AS adresse FROM parcelle;
        '''
    mycursor.execute(sql)
    parcelle = mycursor.fetchall()
    
    return render_template('tickets/edit_ticket.html', ticket=ticket, parcelle=parcelle)

@app.route('/ticket/edit', methods=['POST'])
def valid_edit_ticket():
    mycursor = get_db().cursor()
    id = request.form.get('id', '')
    description = request.form.get('description', '')
    date_incident = request.form.get('date_incident', '')
    statut = request.form.get('statut', '')
    parcelle = request.form.get('parcelle_id', '')
    parcelle_adresse = request.form.get('parcelle_adresse', '')
    tuple_update = (description, date_incident, statut, parcelle, id)
    sql = '''
    UPDATE ticket_incident SET description_incident = %s, date_incident = %s, statut_incident = %s,
        parcelle_concernee = %s WHERE id_ticket = %s;'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()

    message = u'Un ticket modifié, id : '+ id + ' | description : '+ description + \
                ' | date : '+ date_incident + ' | statut : '+ statut + \
                ' | parcelle_concernee : ' + parcelle
    flash(message, 'alert-success')
    return redirect('/ticket/show')

@app.route('/ticket/all')
def show_all_ticket_etat():
    mycursor = get_db().cursor()
    sql = '''
    SELECT COUNT(ticket_incident.id_ticket) AS nombre_ticket,
    SUM(ticket_incident.statut_incident = 'En cours') AS nombre_ticket_en_cours,
    SUM(ticket_incident.statut_incident = 'Résolu') AS nombre_ticket_resolu,
    SUM(ticket_incident.statut_incident = 'A traiter') AS nombre_ticket_en_attente
    FROM ticket_incident LEFT JOIN parcelle ON parcelle.id_parcelle = ticket_incident.parcelle_concernee
    ORDER BY ticket_incident.parcelle_concernee;
    '''
    mycursor.execute(sql)
    ticket_counter = mycursor.fetchall()

    sql = '''
    SELECT ticket_incident.id_ticket AS id,
    ticket_incident.description_incident AS description,
    ticket_incident.date_incident AS date,
    ticket_incident.statut_incident AS statut,
    ticket_incident.parcelle_concernee AS parcelle,
    parcelle.adresse AS adresse FROM ticket_incident LEFT JOIN parcelle ON parcelle.id_parcelle = ticket_incident.parcelle_concernee;
    '''
    mycursor.execute(sql)
    ticket_incident = mycursor.fetchall()

    sql = '''
    SELECT parcelle.id_parcelle AS id,
    parcelle.adresse AS adresse,
    COUNT(ticket_incident.id_ticket) AS nombre_ticket,
    SUM(ticket_incident.statut_incident = 'En cours') AS nombre_ticket_en_cours,
    SUM(ticket_incident.statut_incident = 'Résolu') AS nombre_ticket_resolu,
    SUM(ticket_incident.statut_incident = 'A traiter') AS nombre_ticket_en_attente
    FROM ticket_incident LEFT JOIN parcelle ON parcelle.id_parcelle = ticket_incident.parcelle_concernee
    GROUP BY ticket_incident.parcelle_concernee
    ORDER BY ticket_incident.parcelle_concernee;
    '''
    mycursor.execute(sql)
    ticket_parcelle = mycursor.fetchall()

    max = 0
    for row in ticket_parcelle:
        if row['nombre_ticket'] > max:
            max = row['nombre_ticket']
            parcelle_max = row['id']

    min = 10000000
    for row in ticket_parcelle:
        if row['nombre_ticket'] < min:
            min = row['nombre_ticket']
            parcelle_min = row['id'] 

    sql = '''
    SELECT parcelle.id_parcelle AS id,
    parcelle.adresse AS adresse,
    COUNT(ticket_incident.id_ticket) AS nombre_ticket
    FROM ticket_incident LEFT JOIN parcelle ON parcelle.id_parcelle = ticket_incident.parcelle_concernee
    GROUP BY ticket_incident.parcelle_concernee
    ORDER BY ticket_incident.parcelle_concernee;
    '''
    mycursor.execute(sql)
    ticket_moyenne = mycursor.fetchall()

    labels = [str(row['adresse']) for row in ticket_moyenne]
    values = [int(row['nombre_ticket']) for row in ticket_moyenne]
    total = sum(values)
    values = [int(row['nombre_ticket'])/total for row in ticket_moyenne]
    values = [int(row*100) for row in values]

    return render_template('tickets/show_all_tickets.html', ticket_counter=ticket_counter, ticket_incident=ticket_incident, ticket_parcelle=ticket_parcelle, parcelle_max=parcelle_max, parcelle_min=parcelle_min, labels=labels, values=values)

@app.route('/variete/show')
def show_variete():
    mycursor = get_db().cursor()
    sql = '''
    SELECT variete.id_variete AS id,
    variete.libelle_variete AS nom,
    variete.saison AS saison,
    culture.libelle_culture AS type_culture,
    variete.prix_kg AS prix,
    variete.stock AS stock
    FROM variete, culture
    WHERE culture.id_culture = variete.culture;
    '''
    mycursor.execute(sql)
    variete = mycursor.fetchall()
    print(variete)
    return render_template('variete/show_variete.html', variete=variete)

@app.route('/variete/etat_show')
def show_etat_variete():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
    culture.libelle_culture AS nom,
    SUM(variete.stock) AS stock,
    SUM(variete.prix_kg*variete.stock) AS prix
    FROM variete
    LEFT JOIN culture ON variete.culture = culture.id_culture
    GROUP BY culture.id_culture
    ORDER BY culture.id_culture;
    '''
    mycursor.execute(sql)
    stock = mycursor.fetchall()

    sql ='''
    SELECT  culture.libelle_culture AS culture
    FROM culture
    LEFT JOIN variete ON culture.id_culture = variete.culture
    GROUP BY culture.id_culture
    ORDER BY culture.id_culture;
    '''
    mycursor.execute(sql)
    variete = mycursor.fetchall()

    labels = [str(row['culture']) for row in variete]
    return render_template('variete/etat_variete.html', stock=stock, variete=variete,
                           labels=labels)


@app.route('/variete/add', methods=['GET'])
def add_variete():
    mycursor = get_db().cursor()
    sql='''
    SELECT culture.id_culture AS id_culture, culture.libelle_culture AS nom FROM culture;
    '''
    mycursor.execute(sql)
    culture = mycursor.fetchall()
    sql = '''
    SELECT saison.saison AS saison FROM saison;
    '''
    mycursor.execute(sql)
    saison = mycursor.fetchall()
    return render_template('variete/add_variete.html', culture=culture, saison=saison)


@app.route('/variete/add', methods=['POST'])
def valid_add_variete():
    mycursor = get_db().cursor()

    libelle_variete = request.form.get('libelle_variete', '')
    saison = request.form.get('saison', '')
    culture = request.form.get('culture', '')
    prix_kg = request.form.get('prix_kg', '')
    stock = request.form.get('stock', '')
    tuple_insert = (libelle_variete, saison, culture, prix_kg, stock)

    sql = '''
    INSERT INTO variete(libelle_variete, saison, culture, prix_kg, stock)
    VALUES (%s, %s, %s, %s);
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    message = u'Nouvelle variété , nom : '+libelle_variete + ' | saison : ' + saison + \
              ' | culture : ' + culture+ '| prix/kg : '+ prix_kg + ' | stock : ' + stock
    flash(message, 'alert-success')
    return redirect('/variete/show')


@app.route('/variete/delete', methods=['GET'])
def delete_variete():
    mycursor = get_db().cursor()
    id_variete = request.args.get('id', '')
    tuple_delete = (id_variete)
    sql = '''
    DELETE FROM variete WHERE id_variete = %s;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    message=u'une variété supprimée, id : ' + id_variete
    flash(message, 'alert-warning')
    return redirect('/variete/show')

@app.route('/variete/edit', methods=['GET'])
def edit_variete():
    mycursor = get_db().cursor()

    sql = '''
            SELECT culture.id_culture AS id_culture, culture.libelle_culture AS nom FROM culture;
            '''
    mycursor.execute(sql)
    culture = mycursor.fetchall()

    sql = '''
        SELECT saison.saison AS saison FROM saison;
        '''
    mycursor.execute(sql)
    saison = mycursor.fetchall()

    id = request.args.get('id', '')
    sql = '''
        SELECT variete.id_variete AS id,
        variete.libelle_variete AS nom,
        variete.saison AS saison,
        variete.culture AS culture,
        variete.prix_kg AS prix,
        variete.stock AS stock
        FROM variete, culture
        WHERE variete.id_variete=%s AND culture.id_culture = variete.culture;
        '''
    mycursor.execute(sql, (id))
    variete = mycursor.fetchone()
    return render_template('variete/edit_variete.html', variete=variete, culture=culture, saison=saison)

@app.route('/variete/edit', methods=['POST'])
def valid_edit_variete():
    mycursor = get_db().cursor()
    id = request.form.get('id', '')
    nom = request.form.get('nom', '')
    saison = request.form.get('saison', '')
    culture = request.form.get('culture', '')
    prix = request.form.get('prix_kg', '')
    stock = request.form.get('stock', '')
    tuple_update = (nom, saison, culture, prix, stock, id)
    sql = '''
    UPDATE variete SET libelle_variete = %s, saison = %s, culture = %s,
     prix_kg = %s, stock = %s WHERE id_variete = %s;'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    message = u'Une variété modifiée, id : '+ id + ' | nom : '+ nom + \
              ' | saison : '+ saison + ' | type_culture : '+ culture + \
              ' | prix : ' + prix  + ' | stock : ' + stock
    flash(message, 'alert-success')
    return redirect('/variete/show')

@app.route('/collecte/show')
def show_collecte():
    mycursor = get_db().cursor()
    sql='''   
    SELECT id_collecte AS id,
    quantite_collecte AS quantite,
    produit_collecte AS produit,
    date_collecte AS date,
    id_parcelle AS parcelle_id
    FROM collecte;
    '''
    mycursor.execute(sql)
    collectes = mycursor.fetchall()
    return render_template('collecte/show_collecte.html', collectes=collectes)

@app.route('/collecte/add', methods=['GET'])
def add_collecte():
    mycursor = get_db().cursor()
    sql='''
    SELECT  id_parcelle AS id , adresse      
    FROM parcelle;   
    '''
    mycursor.execute(sql)
    parcelles = mycursor.fetchall()
    return render_template('collecte/add_collecte.html', parcelles=parcelles)

@app.route('/collecte/add', methods=['POST'])
def valid_add_collecte():
    mycursor = get_db().cursor()
    parcelle_id = request.form.get('parcelle_id', '')
    quantite = request.form.get('quantite', '')
    produit = request.form.get('produit', '')
    date = request.form.get('date', '')
    tuple_insert = (parcelle_id, quantite, produit, date)
    sql='''
    INSERT INTO collecte(id_parcelle, quantite_collecte, produit_collecte, date_collecte)
    VALUES (%s, %s, %s, %s);
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'Nouvelle collecte , quantite : '+quantite + ' | produit : ' + produit + ' | date : ' + date + '| parcelle_id : '+ parcelle_id
    flash(message, 'alert-success')
    return redirect('/collecte/show')

@app.route('/collecte/delete', methods=['GET'])
def delete_collecte():
    mycursor = get_db().cursor()
    id = request.args.get('id', '')
    tuple_delete = (id)
    sql = '''
    DELETE FROM collecte WHERE id_collecte = %s;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    message=u'une collecte supprimée, id : ' + id
    flash(message, 'alert-warning')
    return redirect('/collecte/show')

@app.route('/collecte/edit', methods=['GET'])
def edit_collecte():
    mycursor = get_db().cursor()
    id = request.args.get('id', '')
    sql='''
    SELECT id_collecte AS id,
    quantite_collecte AS quantite,
    produit_collecte AS produit,
    date_collecte AS date,
    id_parcelle AS parcelle_id
    FROM collecte
    WHERE id_collecte = %s;
    '''
    mycursor.execute(sql, id)
    collectes = mycursor.fetchall()

    parcelle_id = request.args.get('parcelle_id', '')
    sql='''
    SELECT id_parcelle AS id ,adresse FROM parcelle;
    '''
    mycursor.execute(sql)
    parcelles = mycursor.fetchall()
    return render_template('collecte/edit_collecte.html', collectes=collectes ,parcelles=parcelles)

@app.route('/collecte/edit', methods=['POST'])
def valid_edit_collecte():
    mycursor = get_db().cursor()
    id = request.form.get('id', '')
    parcelle_id = request.form.get('parcelle_id', '')
    quantite = request.form.get('quantite', '')
    produit = request.form.get('produit', '')
    date = request.form.get('date', '')
    tuple_update = (parcelle_id, quantite, produit, date, id)
    sql='''
    UPDATE collecte
    SET id_parcelle = %s, quantite_collecte = %s, produit_collecte = %s, date_collecte = %s
    WHERE id_collecte = %s;
    '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    message = u'Une collecte modifiée, quantite : ' + quantite + ' | produit : ' + produit + ' | date : ' + date + '| parcelle_id : ' + parcelle_id
    flash(message, 'alert-success')

    return redirect('/collecte/show')
    
@app.route('/collecte/all')
def show_collecte_etat():
    mycursor = get_db().cursor()
    sql = '''
    SELECT produit_collecte AS produit, SUM(quantite_collecte) AS quantite
    FROM collecte
    GROUP BY produit_collecte
    ORDER BY produit_collecte;
    '''

    mycursor.execute(sql)
    quantite = mycursor.fetchall()

    sql = '''
    SELECT parcelle.id_parcelle AS id, parcelle.adresse AS adresse, produit_collecte AS produit, SUM(quantite_collecte) AS quantite
    FROM collecte
    LEFT JOIN parcelle ON collecte.id_parcelle = parcelle.id_parcelle
    GROUP BY parcelle.id_parcelle, produit_collecte
    ORDER BY parcelle.id_parcelle;
    '''

    mycursor.execute(sql)
    quantite_parcelle = mycursor.fetchall()

    sql = '''
    SELECT parcelle.id_parcelle AS id, parcelle.adresse AS adresse, SUM(quantite_collecte) AS quantite
    FROM collecte
    LEFT JOIN parcelle ON collecte.id_parcelle = parcelle.id_parcelle
    GROUP BY parcelle.id_parcelle
    ORDER BY parcelle.id_parcelle;
    '''

    mycursor.execute(sql)
    quantite_parcelle_total = mycursor.fetchall()

    # Parcelle max et parcelle min
    max = 0
    for row in quantite_parcelle_total:
        if row['quantite'] > max:
            max = row['quantite']
            parcelle_max = row['id']

    min = 10000000
    for row in quantite_parcelle_total:
        if row['quantite'] < min:
            min = row['quantite']
            parcelle_min = row['id']

    return render_template('collecte/show_collecte_etat.html', quantite=quantite, quantite_parcelle=quantite_parcelle, quantite_parcelle_total=quantite_parcelle_total, parcelle_max=parcelle_max, parcelle_min=parcelle_min)

@app.route('/interaction/show')
def show_interaction():
    mycursor = get_db().cursor()
    sql = '''
    SELECT Interactions.id_interaction AS id, cat.libelle_cat_interaction, description_interaction, prix, date_interaction, Adherent.prenom, Adherent.nom
    FROM
        Interactions 
        LEFT JOIN
            Categorie_Interactions AS cat
            ON Interactions.id_cat_interaction = cat.id_cat_interaction
        LEFT JOIN
            Adherent
            ON Interactions.id_adherent = Adherent.id_adherent
    ORDER BY Adherent.nom
    '''
    mycursor.execute(sql)
    interaction = mycursor.fetchall()
    print(interaction)
    return render_template('interaction/show_interaction.html', interaction=interaction)

@app.route('/interaction/etat_show')
def show_etat_interaction():
    mycursor = get_db().cursor()
    sql = '''
    SELECT id_parcelle, COUNT(id_parcelle) AS total, FORMAT(100 * COUNT(id_parcelle) / (SELECT COUNT(*) FROM a_interagi_sur), 2) AS prop_par_parcelle
    FROM
        a_interagi_sur
    GROUP BY id_parcelle
    ;
    '''
    mycursor.execute(sql)
    prop = mycursor.fetchall()


    labels = [str(row['parcelle']) for row in prop]
    return render_template('interaction/etat_interaction.html', prop=prop,
                           labels=labels)


@app.route('/interaction/add', methods=['GET'])
def add_interaction():
    mycursor = get_db().cursor()
    sql='''
    SELECT id_cat_interaction AS id_cat, libelle_cat_interaction AS descr
    FROM
        Categorie_interactions
    ;
    '''
    mycursor.execute(sql)
    cat = mycursor.fetchall()

    sql = '''
    SELECT id_adherent, prenom, nom
    FROM
        Adherent;
    '''
    mycursor.execute(sql)
    adherent = mycursor.fetchall()

    sql = '''
        SELECT id_parcelle, adresse
        FROM
            Parcelle;
        '''
    mycursor.execute(sql)
    parcelle = mycursor.fetchall()
    return render_template('interaction/add_interaction.html', cat=cat, adherent=adherent, parcelle=parcelle)


@app.route('/interaction/add', methods=['POST'])
def valid_add_interaction():
    mycursor = get_db().cursor()

    description_interaction = request.form.get('description_interaction', '')
    date_interaction = request.form.get('date_interaction', '')
    prix = request.form.get('prix', '')
    id_cat_interaction = request.form.get('id_cat_interaction', '')
    id_adherent = request.form.get('id_adherent', '')
    tuple_insert1 = (description_interaction, date_interaction, prix, id_cat_interaction, id_adherent)

    sql = '''
    INSERT INTO Interactions(description_interaction, date_interaction, prix, id_cat_interaction, id_adherent)
    VALUES (%s, %s, %s, %s, %s);
    '''
    mycursor.execute(sql, tuple_insert1)
    get_db().commit()

    sql = '''
            SELECT MAX(id_interaction)
            FROM 
                Interactions
            '''
    mycursor.execute(sql)
    id_interaction = mycursor.fetchone()

    id_parcelle = request.form.get('id_parcele', '')
    tuple_insert2 = (id_parcelle, id_interaction)

    sql = '''
    INSERT INTO a_interagi_sur(id_parcelle, id_interaction)
    VALUES (%s, %s)
    '''
    mycursor.execute(sql, tuple_insert2)
    get_db().commit()

    message = u'Nouvelle interaction , description : ' + description_interaction + ' | date : ' + date_interaction + \
              ' | prix : ' + prix + '| catégorie : ' + id_cat_interaction + ' | adhérent : ' + id_adherent + ' | parcelle : ' + id_parcelle
    flash(message, 'alert-success')
    return redirect('/interaction/show')


@app.route('/interaction/delete', methods=['GET'])
def delete_interaction():
    mycursor = get_db().cursor()
    id_interaction = request.args.get('id', '')
    tuple_delete = (id_interaction)
    sql = '''
    DELETE
    FROM 
        Interactions
    WHERE
        id_interaction = %s
    ;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    message=u'une interaction supprimée, id : ' + id_interaction
    flash(message, 'alert-warning')
    return redirect('/interaction/show')

@app.route('/interaction/edit', methods=['GET'])
def edit_interaction():
    mycursor = get_db().cursor()
    sql = '''
        SELECT id_cat_interaction AS id_cat, libelle_cat_interaction AS descr
        FROM
            Categorie_interaction
        ;
        '''
    mycursor.execute(sql)
    cat = mycursor.fetchall()

    sql = '''
        SELECT id_adherent, prenom, nom
        FROM
            Adherent;
        '''
    mycursor.execute(sql)
    adherent = mycursor.fetchall()

    sql = '''
            SELECT id_parcelle, adresse
            FROM
                Parcelle;
            '''
    mycursor.execute(sql)
    parcelle = mycursor.fetchall()

    id = request.args.get('id', '')
    sql = '''
        SELECT id_interaction AS id, description_interaction, date_interaction, prix, id_cat_interaction, id_adherent, a_interagi_sur.id_parcelle
        FROM 
            Interactions, a_interagi_sur
        WHERE id_interaction=%s AND a_interagi_sur.id_interaction = id_interaction;
        '''
    mycursor.execute(sql, (id))
    interaction = mycursor.fetchone()
    return render_template('interaction/edit_interaction.html', interaction=interaction, cat=cat, adherent=adherent, parcelle=parcelle)



@app.route('/interaction/edit', methods=['POST'])
def valid_edit_interaction():
    mycursor = get_db().cursor()

    id = request.form.get('id', '')
    description_interaction = request.form.get('description_interaction', '')
    date_interaction = request.form.get('date_interaction', '')
    prix = request.form.get('prix', '')
    id_cat_interaction = request.form.get('id_cat_interaction', '')
    id_adherent = request.form.get('id_adherent', '')
    tuple_update1 = (description_interaction, date_interaction, prix, id_cat_interaction, id_adherent, id)

    sql = '''
    UPDATE Interactions SET description_interaction = %s, date_interaction = %s, prix = %s, id_cat_interaction = %s, id_adherent = %s
    WHERE 
        id_interaction = %s
    ;
    '''
    mycursor.execute(sql, tuple_update1)
    get_db().commit()

    id_parcelle = request.form.get('id_parcelle', '')
    tuple_update2 = (id_parcelle, id)

    sql = '''
        UPDATE a_interagi_sur SET id_parcelle = %s
        WHERE 
            id_interaction = %s
        ;
        '''
    mycursor.execute(sql, tuple_update2)
    get_db().commit()

    message = u'Une interaction modifiée, id : ' + id + ' | description : ' + description_interaction + ' | date : ' + date_interaction + \
              ' | prix : ' + prix + '| catégorie : ' + id_cat_interaction + ' | adhérent : ' + id_adherent + ' | parcelle : ' + id_parcelle
    flash(message, 'alert-success')
    return redirect('/interaction/show')


if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=5000)
