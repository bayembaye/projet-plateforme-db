/** Reponses aux questions de l'exercice **/ 

-- Question 1 
 -- Modele Relationnel textuel
	/** 
		Categories( @idCateg , nomCateg , TVA) 
		Commandes( @idCde, DAteCde, EtatCde) 
		BeneficeCumul( @idProduit# , Cumul)
		Produits( @idProduit, nomProduit, QteStock, PrixA, 
			PrixV, StockMin, idCateg#)
		Contient ( @idProduit# , @idCde# , QteCde) 

	**/
 -- Script SQL 
 /** Creation de la Base de donnees **/
 CREATE DATABASE IF NOT EXISTS GestionCommerciale ;
 USE GestionCommerciale ;

 /** Creation des tables de la base de données **/
-- Creation de la table Categorie
CREATE TABLE IF NOT EXISTS Categorie (
	idCateg integer auto_increment PRIMARY KEY, 
	nomCateg varchar(50),
	TVA integer
);

 -- Creation de la table Commandes
CREATE TABLE IF NOT EXISTS Commandes(
	idCde integer auto_increment PRIMARY KEY,
	DateCde date ,
	EtatCde boolean default FALSE
);
