/** Question Theoriques  **/

-- Question 1 : Modele Logique 
/** 
 Realisateur (@NoReal, Nom , Prenom, DateN, DateM, Nationalite, Biographie) 
 Acteur ( @NoAct, Nom , Prenom, DateN, DateM, Nationalite, Biographie)
 Film (@NoFilm, TireFr, TitreO , Annee , typeF , Duree, Histoire, Commentaire)
 Genre ( @GenreRef )
 Exemplaire ( @NoExp, Dispo, NoFilm#, NoClient# , DateEmprunt)
 Client (@NoClient, Nom, Prenom, Adresse, Tel)
 est_de ( @GenreRef# , @NoFilm# )
 a_mis_en_scene ( @NoReal# , @NoFilm#)
 joue_dans (@NoFilm# , @NoAct#)
**/

--Question 2 : Creation de la base de donnee et de son administrateur
 -- Rqe: Nous supposons dans la suite du script que l'utilisateur en cours est le root
-- Creation de la base de donnees
 create database GestCinema ; 
-- creation de l'administrateur de la base
 create user admin@"localhost" identified by "Passer2025" ;
-- octroie des privileges a l'administrateur 
 GRANT ALL PRIVILEGES on GestCinema.* to admin@"localhost" ; 
-- Creation des tables de la base de donnees 
 use GestCinema ;
 CREATE TABLE  Realisateur (
	NoReal integer auto_increment Primary Key,
	Nom varchar(100) ,
	Prenom varchar(100), 
	DateN Date, 
	DateM Date, 
	Nationalite varchar(100),
	Biographie text);
 

/** Questions SQL **/



CREATE TABLE Acteur (
    NoAct integer auto_increment Primary Key,
    Nom varchar(100),
    Prenom varchar(100), 
    DateN Date, 
    DateM Date, 
    Nationalite varchar(100),
    Biographie text
);


CREATE TABLE Film (
    NoFilm integer auto_increment Primary Key,
    TireFr varchar(100),
    TitreO varchar(100),
    Annee integer,
    typeF varchar(100),
    Duree integer,
    Histoire text,
    Commentaire text
);


CREATE TABLE Genre (
    GenreRef integer auto_increment Primary Key,
    NomGenre varchar(100)
);


CREATE TABLE Exemplaire (
    NoExp integer auto_increment Primary Key,
    Dispo boolean,
    NoFilm integer,
    NoClient integer,
    DateEmprunt Date,
    FOREIGN KEY (NoFilm) REFERENCES Film(NoFilm),
    FOREIGN KEY (NoClient) REFERENCES Client(NoClient)
);

-- Table Client
CREATE TABLE Client (
    NoClient integer auto_increment Primary Key,
    Nom varchar(100),
    Prenom varchar(100),
    Adresse varchar(200),
    Tel varchar(15)
);


CREATE TABLE est_de (
    GenreRef integer,
    NoFilm integer,
    PRIMARY KEY (GenreRef, NoFilm),
    FOREIGN KEY (GenreRef) REFERENCES Genre(GenreRef),
    FOREIGN KEY (NoFilm) REFERENCES Film(NoFilm)
);


CREATE TABLE a_mis_en_scene (
    NoReal integer,
    NoFilm integer,
    PRIMARY KEY (NoReal, NoFilm),
    FOREIGN KEY (NoReal) REFERENCES Realisateur(NoReal),
    FOREIGN KEY (NoFilm) REFERENCES Film(NoFilm)
);

CREATE TABLE joue_dans (
    NoFilm integer,
    NoAct integer,
    PRIMARY KEY (NoFilm, NoAct),
    FOREIGN KEY (NoFilm) REFERENCES Film(NoFilm),
    FOREIGN KEY (NoAct) REFERENCES Acteur(NoAct)
);


1. Quels clients (Numero, Nom et Prenom) ont emprunté tous les films avec l’acteur Modou FALL ?

Requête SQL :

SELECT DISTINCT c.NoClient, c.Nom, c.Prenom
FROM Client c
WHERE NOT EXISTS (
    SELECT f.NoFilm
    FROM Film f
    JOIN joue_dans jd ON f.NoFilm = jd.NoFilm
    JOIN Acteur a ON jd.NoAct = a.NoAct
    WHERE a.Nom = 'FALL' AND a.Prenom = 'Modou'
    AND NOT EXISTS (
        SELECT e.NoExp
        FROM Exemplaire e
        WHERE e.NoFilm = f.NoFilm AND e.NoClient = c.NoClient
    )
);

Algèbre relationnelle :

π NoClient, Nom, Prenom (Client) - π NoClient, Nom, Prenom (
  Client ⨝ (Exemplaire ⨝ Film ⨝ (joue_dans ⨝ (Acteur ⨝ σ Nom='FALL' ∧ Prenom='Modou' (Acteur)))))
)

2. Quel est le réalisateur le plus âgé ?

Requête SQL :

SELECT Nom, Prenom, MIN(DateN) AS Age
FROM Realisateur
GROUP BY Nom, Prenom
ORDER BY Age ASC
LIMIT 1;


Algèbre relationnelle :

π Nom, Prenom, MIN(DateN) (Realisateur) ⨝ (Realisateur ⨝ π MIN(DateN) (Realisateur))


3. Quel genre de film a le plus grand nombre d’exemplaires ?

Requête SQL :

SELECT g.NomGenre, COUNT(e.NoExp) AS NombreExemplaires
FROM Genre g
JOIN est_de ed ON g.GenreRef = ed.GenreRef
JOIN Film f ON ed.NoFilm = f.NoFilm
JOIN Exemplaire e ON e.NoFilm = f.NoFilm
GROUP BY g.NomGenre
ORDER BY NombreExemplaires DESC
LIMIT 1;


Algèbre relationnelle :

π NomGenre, COUNT(NoExp) (
  Genre ⨝ est_de ⨝ Film ⨝ Exemplaire
)


4. Combien d’acteurs ont joué dans des films de Science-Fiction ?

Requête SQL :

SELECT COUNT(DISTINCT a.NoAct) 
FROM Acteur a
JOIN joue_dans jd ON a.NoAct = jd.NoAct
JOIN Film f ON jd.NoFilm = f.NoFilm
JOIN est_de ed ON f.NoFilm = ed.NoFilm
JOIN Genre g ON ed.GenreRef = g.GenreRef
WHERE g.NomGenre = 'Science-Fiction';



Algèbre relationnelle :

COUNT(π NoAct (
  Acteur ⨝ (joue_dans ⨝ (Film ⨝ (est_de ⨝ (Genre ⨝ σ NomGenre='Science-Fiction' (Genre)))))
))


5. Quels sont les réalisateurs qui ont joué dans des films qu’ils ont mis en scène (Même Nom et Prénom) ?

Requête SQL :


SELECT r.Nom, r.Prenom
FROM Realisateur r
JOIN a_mis_en_scene am ON r.NoReal = am.NoReal
JOIN Film f ON am.NoFilm = f.NoFilm
JOIN joue_dans jd ON f.NoFilm = jd.NoFilm
JOIN Acteur a ON jd.NoAct = a.NoAct
WHERE r.Nom = a.Nom AND r.Prenom = a.Prenom;


Algèbre relationnelle :

π Nom, Prenom (
  Realisateur ⨝ (a_mis_en_scene ⨝ (Film ⨝ (joue_dans ⨝ Acteur))))
)

6. Donnez les noms et prénoms des personnes représentées dans la base de données (Réalisateur, Acteur, Client), ainsi que leur type « Real » / « Act » / « Client »

Requête SQL :

SELECT Nom, Prenom, 'Real' AS Type
FROM Realisateur
UNION
SELECT Nom, Prenom, 'Act' AS Type
FROM Acteur
UNION
SELECT Nom, Prenom, 'Client' AS Type
FROM Client;
```

Algèbre relationnelle :

π Nom, Prenom, 'Real' (
  Realisateur
) ∪ π Nom, Prenom, 'Act' (
  Acteur
) ∪ π Nom, Prenom, 'Client' (
  Client
)


### 7. Quels sont les genres de films jamais empruntés par Fatou NDIAYE ?

Requête SQL :

SELECT g.NomGenre
FROM Genre g
WHERE NOT EXISTS (
    SELECT e.NoExp
    FROM Exemplaire e
    JOIN Film f ON e.NoFilm = f.NoFilm
    JOIN est_de ed ON f.NoFilm = ed.NoFilm
    WHERE ed.GenreRef = g.GenreRef AND e.NoClient = (
        SELECT NoClient FROM Client WHERE Nom = 'NDIAYE' AND Prenom = 'Fatou'
    )
);


**Algèbre relationnelle :

π NomGenre (
  Genre - π NomGenre (
    Genre ⨝ (Exemplaire ⨝ Film ⨝ (est_de ⨝ σ Nom='NDIAYE' ∧ Prenom='Fatou' (Client)))
  )
)

8. En supposant que deux individus ayant les mêmes noms et prénoms sont la même personne, quels acteurs ont emprunté les films dans lesquels ils ont joué ?

Requête SQL :

SELECT DISTINCT a.NoAct, a.Nom, a.Prenom
FROM Acteur a
JOIN joue_dans jd ON a.NoAct = jd.NoAct
JOIN Exemplaire e ON e.NoFilm = jd.NoFilm
WHERE e.NoClient = a.NoAct;

Algèbre relationnelle :

π NoAct, Nom, Prenom (
  Acteur ⨝ (joue_dans ⨝ (Exemplaire ⨝ σ NoClient=NoAct (Exemplaire)))
)


9. Avec la même supposition que précédemment, quels acteurs ne sont pas des clients ?

Requête SQL :
sql
SELECT DISTINCT a.NoAct, a.Nom, a.Prenom
FROM Acteur a
WHERE NOT EXISTS (
    SELECT e.NoClient
    FROM Exemplaire e
    WHERE e.NoClient = a.NoAct
);


Algèbre relationnelle :

π NoAct, Nom, Prenom (
  Acteur - π NoAct, Nom, Prenom (
    Acteur ⨝ Exemplaire
  )
)

10. Quels sont les 5 nationalités des acteurs qui ont eu le plus de films empruntés ?

Requête SQL :

SELECT a.Nationalite, COUNT(e.NoExp) AS NombreEmprunts
FROM Acteur a
JOIN joue_dans jd ON a.NoAct = jd.NoAct
JOIN Film f ON jd.NoFilm = f.NoFilm
JOIN Exemplaire e ON e.NoFilm = f.NoFilm
GROUP BY a.Nationalite
ORDER BY NombreEmprunts DESC
LIMIT 5;

Algèbre relationnelle :

π Nationalite, COUNT(NoExp) (
  Acteur ⨝ (joue_dans ⨝ (Film ⨝ Exemplaire))
)






INSERT INTO Client (Nom, Prenom, DateNaissance)
VALUES 
    ('NDIAYE', 'Fatou', '1995-06-15'),
    ('SOW', 'Mamadou', '1988-11-02'),
    ('DIOP', 'Aissatou', '2000-03-21');










Rappels SQL : 

Structured Query Language  est divisé en 3 languages 

LDD : Language de Definition de Données
  Gérer les Structures des informations qui sont stockées 

LMD : Language de Manipulation de Données
	Gérer les données qui sont stockées sans avoir à modifier leurs structures

LED : Language d’Extraction de Données
	Permet d’extraire et mettre en forme les données qui sont renvoyées à l’utilisateur

En terme de syntaxe les différents languages ont la même base : 

MOTCLEF <Parametres>  ;

MOTCLEF : Primitive assertionelle qui donne un ordre au SGBD

;  : Caractère de fin de commande par défaut  ( modifiable) 


LDD: 
	CREATE
	ALTER
	DROP 

LMD: 
	INSERT
	UPDATE 
	DELETE 


LED: 
	SELECT

On peut avoir des details sur sa syntaxe dans mysql. En utilisant la commande « help Primitive »

SELECT <Output>
FROM <INPUT>
[OPTIONS ] ;


<OUTPUT> : 
* : Tous les champs 
<NomChamp> : champ choisi de façon explicite 
DISTINCT <NomChamp> : permet d’éviter les répétitions	de tuples ( ou d’enregistrement )
<Liste deChamps> : Doivent être séparés par des virgules et l’ordre est personnalisé 
<Constantes> : Quelque soit le type de données de la constante
<ReqImbriquée>: Requête qui ne renverra qu’une seule valeur scalaire équivalente à une constante


[OPTIONS]
LIMIT : permet de limiter le nombre d’enregistrements à afficher
	- limit nbEnregistrements
	- limit Saut nbEnregistrements

ORDER BY : permet de trier les informations en fonction de champs choisis
	- champ ASC / DESC  (ASC: Ascendant ; DESC : Descendant )
	- champ1 , Champ2 , ChamP3 ( Par défaut si aucun sens n’est cité, les champs sont triés en ASC )

Exemple : Citer les 3 numéros d’employés les plus payés sans utiliser la fonction max
			 Citer les 3 numéros d’employés les moins payés sans utiliser la fonction min 
Rqe: utiliser la table salaries


Mesurer la difference entre le salaire Max et le salaire des employés en ne montrant que les 10 personnes qui sont les plus éloignés du salaire max 

GROUP BY: permet de regrouper les enregistrements en fonction de valeurs de champ pour effectuer des calculs

Exercice : Proposez les requêtes SQL permettant de répondre aux questions suivantes : 
- Age moyen des employes
- les 3 femmes les plus agées de l'entreprise
- les 7e, 8e et 9e homme les moins ages
- les 5 employes les plus anciens et leur moyenne d'age
- A partir de titles quel est le numero d'employe qui a le plus duré dans un poste

<INPUT>
« Dual » ou (Vide) :  Pas de source de données ( pile système)
Table  : 
	Table existant dans la base de données en cours, sinon elle sera précédée du nom de la bdd où elle est située
Vue :
	Résultat de l’execution d’une requête où l’expression est stockée . Elles sont utilisables en consultation comme les tables
	Exemple :  CREATE VIEW <NomVue> AS  SELECT …. ;
					SELECT * from <NomVue>… ;
SousRequête 
	Exemple :   SELECT *  FROM ( SELECT * FROM Table WHERE Cond ) as <Alias> ;

Expressions combinant ( Table / Vue / Sous Requête)
  * Produit cartésien :   SELECT * FROM Table1 , Table2 ; ( Attention au produit des enregistrements et à l’explosion de l’utilisation de la mémoire )
 * Jointure  ou ( Thêta-jointure):  SELECT * FROM Table1. join Table2 on Table1.champ3 = Table2.champ3 ; 
*  Jointure natural : SELECT * FROM Table1 natural join Table2 ; 

Remarque : Equivalences entre Produit cartésien et Thêta-jointure

mysql> select * from employees e , salaries s where e.emp_no =s.emp_no  ;
ou 
mysql> select * from employees e join  salaries s on e.emp_no =s.emp_no  ;










