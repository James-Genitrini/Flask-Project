DROP TABLE IF EXISTS a_interagi_sur, Interactions, Categorie_Interactions, Adherent, collecte, ticket_incident, parcelle, variete, culture, saison;

CREATE TABLE saison (
    saison VARCHAR(31),
    PRIMARY KEY(saison)
);

CREATE TABLE culture (
    id_culture INT AUTO_INCREMENT,
    libelle_culture VARCHAR(255),
    PRIMARY KEY(id_culture)
);

CREATE TABLE variete (
    id_variete INT AUTO_INCREMENT,
    libelle_variete VARCHAR(255),
    saison VARCHAR(31),
    culture INT,
    prix_kg DECIMAL(4,2),
    stock DECIMAL(4,2),
    PRIMARY KEY(id_variete),
    FOREIGN KEY(saison) REFERENCES saison(saison),
    FOREIGN KEY(culture) REFERENCES culture(id_culture)
);
CREATE TABLE parcelle (
    id_parcelle INT AUTO_INCREMENT,
    surface DECIMAL(4,2),
    adresse VARCHAR(255),
    PRIMARY KEY(id_parcelle)
);

CREATE TABLE ticket_incident (
    id_ticket INT AUTO_INCREMENT,
    description_incident VARCHAR(255),
    date_incident DATE,
    statut_incident VARCHAR(31),
    parcelle_concernee INT,
    PRIMARY KEY(id_ticket),
    FOREIGN KEY(parcelle_concernee) REFERENCES parcelle(id_parcelle)
);

CREATE TABLE collecte(
   id_collecte INT AUTO_INCREMENT,
   quantite_collecte DECIMAL(4,2),
   produit_collecte VARCHAR(50),
   date_collecte DATETIME,
   id_parcelle INT NOT NULL,
   PRIMARY KEY(id_collecte) ,
   FOREIGN KEY(id_parcelle) REFERENCES parcelle(id_parcelle)
);

CREATE TABLE Adherent(
    id_adherent INT AUTO_INCREMENT,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    adresse_adherent VARCHAR(255),
    PRIMARY KEY(id_adherent)
);

CREATE TABLE Categorie_Interactions(
    id_cat_interaction INT AUTO_INCREMENT,
    libelle_cat_interaction VARCHAR(255),
    PRIMARY KEY(id_cat_interaction)
);

CREATE TABLE Interactions(
    id_interaction INT AUTO_INCREMENT,
    description_interaction VARCHAR(255),
    date_interaction DATETIME,
    prix DECIMAL(10,2),
    id_cat_interaction INT,
    id_adherent INT,
    PRIMARY KEY(id_interaction),
    FOREIGN KEY(id_cat_interaction) REFERENCES Categorie_Interactions(id_cat_interaction),
    FOREIGN KEY(id_adherent) REFERENCES Adherent(id_adherent)
);

CREATE TABLE a_interagi_sur(
    id_parcelle INT,
    id_interaction INT,
    PRIMARY KEY(id_parcelle, id_interaction),
    FOREIGN KEY(id_parcelle) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY(id_interaction) REFERENCES Interactions(id_interaction)
);


INSERT INTO saison VALUES
   ('Printemps'),
   ('Ete'),
   ('Automne'),
   ('Hiver');

INSERT INTO culture VALUES
    (1, 'Tomates'),
    (2, 'Pommes'),
    (3, 'Poires'),
    (4, 'Maïs'),
    (5, 'Blé'),
    (6, 'Carottes');

INSERT INTO variete VALUES
    (1, 'Carottes de Nantes', 'Ete', 6, 1.5, 74.5),
    (2, 'Tomates cerises', 'Ete', 1, 5.67, 52.0),
    (3, 'Pommes Gala', 'Hiver', 2, 1.95, 0),
    (4, 'Poires Williams', 'Ete', 3, 3.99, 5.8);

INSERT INTO parcelle VALUES 
    (NULL, 23.5, '1 rue de la Paix'),
    (NULL, 17.5, '2 rue de la Guerre'),
    (NULL, 45.5, '78 rue des Lilas'),
    (NULL, 4.5, '243 rue du Lavoir'),
    (NULL, 5.5, '80 rue des petites chevres'),
    (NULL, 6.5, '6127 rue du R warwick'),
    (NULL, 4.5, '69 avenue de Lyon'),
    (NULL, 0.10, '5 rue du Piratier'),
    (NULL, 7.8, '7 chemin du chinoa');

INSERT INTO ticket_incident VALUES
    (NULL, 'Incendie', '2020-09-27', 'En cours', 1),
    (NULL, 'Inondation', '2020-09-27', 'En cours', 2),
    (NULL, 'Le pommier est tombe :(', '2020-09-27', 'En cours', 3),
    (NULL, 'Squatteurs', '2020-09-27', 'En cours', 4),
    (NULL, 'Taupes', '2020-09-27', 'En cours', 5),
    (NULL, 'Encore des taupes', '1998-03-24', 'A traiter', 2),
    (NULL, 'Geplusdidee', '2020-09-27', 'En cours', 6);
    

INSERT INTO collecte VALUES (1, 23.5, 'Carottes', '2023-09-27',1),
    (2, 17.5, 'Tomates', '2020-08-14 12:00:00',1),
    (3, 45.5, 'Pommes', '2020-10-02 12:36:45',2),
    (4, 4.5, 'Poires', '2020-09-27 23:54:13',3),
    (5, 5.5, 'Carottes', '2020-09-27 09:08:23',4),
    (6, 6.5, 'Tomates', '2020-09-27 23:12:13',5),
    (7, 4.5, 'Pommes', '2020-09-27 03:02:01',6),
    (8, 0.10, 'Poires', '2020-09-27 07:07:07',7),
    (9, 7.8, 'Carottes', '2020-09-27 08:27:43',8);

INSERT INTO Adherent VALUES
    (NULL, 'Dupont', 'Jean', '1 rue de la Paix'),
    (NULL, 'Dupont', 'Jean', '2 rue de la Guerre'),
    (NULL, 'Dupont', 'Jean', '78 rue des Lilas'),
    (NULL, 'Dupont', 'Jean', '243 rue du Lavoir'),
    (NULL, 'Dupont', 'Jean', '80 rue des petites chevres'),
    (NULL, 'Dupont', 'Jean', '6127 rue du R warwick'),
    (NULL, 'Dupont', 'Jean', '69 avenue de Lyon'),
    (NULL, 'Dupont', 'Jean', '5 rue du Piratier'),
    (NULL, 'Dupont', 'Jean', '7 chemin du chinoa');

INSERT INTO Categorie_Interactions VALUES
    (NULL, 'Arrosgae'),
    (NULL, 'Traitement'),
    (NULL, 'Entretien');

INSERT INTO Interactions VALUES
    (NULL, 'Arrosage', '2020-09-27 12:00:00', 0.0, 1, 1),
    (NULL, 'Traitement', '2020-09-27 12:00:00', 0.0, 2, 2),
    (NULL, 'Entretien', '2020-09-27 12:00:00', 0.0, 3, 3),
    (NULL, 'Arrosage', '2020-09-27 12:00:00', 0.0, 1, 4),
    (NULL, 'Traitement', '2020-09-27 12:00:00', 0.0, 2, 5),
    (NULL, 'Entretien', '2020-09-27 12:00:00', 0.0, 3, 6),
    (NULL, 'Arrosage', '2020-09-27 12:00:00', 0.0, 1, 7),
    (NULL, 'Traitement', '2020-09-27 12:00:00', 0.0, 2, 8),
    (NULL, 'Entretien', '2020-09-27 12:00:00', 0.0, 3, 9);
