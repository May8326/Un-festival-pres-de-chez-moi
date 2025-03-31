# Importation des modules nécessaires
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.app import app, db
from ..models.database import Festival, MonumentHistorique, Commune, relation_user_favori, LieuFestival
from sqlalchemy import and_, func
from ..models.formulaires import AjoutFavori, ModificationFavori, SuppressionFavori
from ..models.users import Users
from random import randint

# Route pour insérer un favori
@app.route("/festivalchezmoi/insertion/favori", methods=['POST'])
@login_required  # Nécessite que l'utilisateur soit connecté
def insertion_favori():
    try:
        # Récupération des données du formulaire
        user_id = current_user.id
        nom_festival = request.form.get("nom_festival")
        nom_monument = request.form.get("nom_monument")
        nom_commune = request.form.get("nom_commune")

        # Initialisation des IDs à None
        festival_id = None
        monument_id = None
        commune_id = None

        # Recherche du festival correspondant au nom fourni
        if nom_festival:
            festival = db.session.query(Festival).filter(func.lower(Festival.nom_festival) == nom_festival.lower()).first()
            if festival:
                festival_id = festival.id_festival

        # Recherche du monument correspondant au nom fourni
        if nom_monument:
            monument = db.session.query(MonumentHistorique).filter(func.lower(MonumentHistorique.nom_monument) == nom_monument.lower()).first()
            if monument:
                monument_id = monument.id_monument_historique

        # Recherche de la commune correspondant au nom fourni
        if nom_commune:
            commune = db.session.query(Commune).filter(func.lower(Commune.nom_commune) == nom_commune.lower()).first()
            if commune:
                commune_id = commune.id_commune

        # Vérification qu'au moins une information a été fournie
        if not (festival_id or monument_id or commune_id):
            flash("Aucune information valide n'a été fournie pour ajouter un favori.", "error")
            return redirect(request.referrer)

        # Log des valeurs insérées
        app.logger.info(f"Valeurs insérées : user_id={user_id}, festival_id={festival_id}, monument_id={monument_id}, commune_id={commune_id}")

        # Vérification si le favori existe déjà
        favori_existant = db.session.query(relation_user_favori).filter(
            and_(
                relation_user_favori.c.user_id == user_id,
                relation_user_favori.c.id_festival == festival_id,
                relation_user_favori.c.id_monument_historique == monument_id,
                relation_user_favori.c.id_commune == commune_id
            )
        ).first()

        if favori_existant:
            flash("Ce favori est déjà enregistré.", "warning")
        else:
            # Génération d'une clé primaire unique pour la relation
            relation_id = int(str(user_id) + str(festival_id) + str(randint(1, 100)))
            # Ajout du favori dans la table relation_user_favori
            db.session.execute(
                relation_user_favori.insert().values(
                    id_relation=relation_id,
                    user_id=user_id,
                    id_festival=festival_id,
                    id_monument_historique=monument_id,
                    id_commune=commune_id
                )
            )
            db.session.commit()
            flash("Favori ajouté avec succès.", "success")

    except Exception as e:
        # Gestion des erreurs et rollback en cas d'échec
        app.logger.error(f"Erreur lors de l'ajout du favori : {str(e)}")
        db.session.rollback()
        flash(f"Une erreur s'est produite lors de l'ajout du favori : {str(e)}", "error")

    # Redirection vers la page précédente
    return redirect(request.referrer)

# Route pour afficher la liste des favoris
@app.route("/festivalchezmoi/liste/favoris", methods=['GET', 'POST'])
@login_required
def liste_favoris():
    try:
        # Log de l'utilisateur connecté
        app.logger.info(f"Utilisateur connecté : {current_user.id} - {current_user.prenom}")

        # Création du formulaire pour ajouter un favori
        form_ajout_favori = AjoutFavori()

        # Traitement du formulaire si soumis
        if form_ajout_favori.validate_on_submit():
            nom = form_ajout_favori.nom.data
            type_favori = form_ajout_favori.type.data

            # Ajout d'une commune comme favori
            if type_favori == 'commune':
                commune = Commune.query.filter(func.lower(Commune.nom_commune) == nom.lower()).first()
                if commune:
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == current_user.id,
                            relation_user_favori.c.id_commune == commune.id_commune
                        )
                    ).first()
                    if not favori_existant:
                        db.session.execute(
                            relation_user_favori.insert().values(
                                user_id=current_user.id,
                                id_commune=commune.id_commune
                            )
                        )
                        db.session.commit()
                        flash(f"La commune '{commune.nom_commune}' a été ajoutée à vos favoris.", "success")
                    else:
                        flash(f"La commune '{commune.nom_commune}' est déjà dans vos favoris.", "warning")
                else:
                    flash(f"Aucune commune trouvée avec le nom '{nom}'.", "error")

            # Ajout d'un monument comme favori
            elif type_favori == 'monument':
                monument = MonumentHistorique.query.filter(func.lower(MonumentHistorique.titre_editorial_de_la_notice) == nom.lower()).first()
                if monument:
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == current_user.id,
                            relation_user_favori.c.id_monument_historique == monument.id_monument_historique
                        )
                    ).first()
                    if not favori_existant:
                        db.session.execute(
                            relation_user_favori.insert().values(
                                user_id=current_user.id,
                                id_monument_historique=monument.id_monument_historique
                            )
                        )
                        db.session.commit()
                        flash(f"Le monument '{monument.nom_monument}' a été ajouté à vos favoris.", "success")
                    else:
                        flash(f"Le monument '{monument.nom_monument}' est déjà dans vos favoris.", "warning")
                else:
                    flash(f"Aucun monument trouvé avec le nom '{nom}'.", "error")

            # Ajout d'un festival comme favori
            elif type_favori == 'festival':
                festival = Festival.query.filter(func.lower(Festival.nom_festival) == nom.lower()).first()
                if festival:
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == current_user.id,
                            relation_user_favori.c.id_festival == festival.id_festival
                        )
                    ).first()
                    if not favori_existant:
                        db.session.execute(
                            relation_user_favori.insert().values(
                                user_id=current_user.id,
                                id_festival=festival.id_festival
                            )
                        )
                        db.session.commit()
                        flash(f"Le festival '{festival.nom_festival}' a été ajouté à vos favoris.", "success")
                    else:
                        flash(f"Le festival '{festival.nom_festival}' est déjà dans vos favoris.", "warning")
                else:
                    flash(f"Aucun festival trouvé avec le nom '{nom}'.", "error")

        # Récupération des favoris de l'utilisateur connecté
        favoris = db.session.query(relation_user_favori).filter(
            relation_user_favori.c.user_id == current_user.id
        ).all()

        # Tri des favoris par type
        favoris_festivals = []
        favoris_monuments = []
        favoris_communes = []

        for favori in favoris:
            # Traitement des festivals
            if favori.id_festival:
                festival = Festival.query.get(favori.id_festival)
                if festival:
                    favoris_festivals.append({
                        "id": festival.id_festival,
                        "nom": festival.nom_festival or "-",
                        "lieu": f"{festival.lieu.commune.nom_commune or '-'} ({str(festival.lieu.commune.code_departement).zfill(2) or '-'})" if festival.lieu and festival.lieu.commune else "-",
                        "type": festival.type.discipline_dominante_festival or "-" if festival.type else "-",
                        "date": festival.dates.periode_principale_deroulement_festival or "-" if festival.dates else "-",
                        "contact": f"<a href='{festival.contact.site_internet_festival}' target='_blank'>Site Internet</a>" if festival.contact and festival.contact.site_internet_festival else "-"
                    })

            # Traitement des monuments
            elif favori.id_monument_historique:
                monument = MonumentHistorique.query.get(favori.id_monument_historique)
                if monument:
                    liens = []
                    if monument.contact and monument.contact.lien_internet_vers_base_palissy:
                        liens.append(f"<a href='{monument.contact.lien_internet_vers_base_palissy}' target='_blank'>Palissy</a>")
                    if monument.contact and monument.contact.lien_internet_vers_base_archiv_mh:
                        liens.append(f"<a href='{monument.contact.lien_internet_vers_base_archiv_mh}' target='_blank'>Base Archiv</a>")
                    if monument.contact and monument.contact.lien_internet_externe:
                        liens.append(f"<a href='{monument.contact.lien_internet_externe}' target='_blank'>Externe</a>")

                    favoris_monuments.append({
                        "id": monument.id_monument_historique,
                        "nom": monument.nom_monument or "-",
                        "lieu": f"{monument.commune.nom_commune or '-'} ({str(monument.commune.code_departement).zfill(2) or '-'})" if monument.commune else "-",
                        "date": monument.dates.datation_edifice or "-" if monument.dates else "-",
                        "contact": ", ".join(liens) if liens else "-"
                    })

            # Traitement des communes
            elif favori.id_commune:
                commune = Commune.query.get(favori.id_commune)
                if commune:
                    favoris_communes.append({
                        "nom": commune.nom_commune or "-",
                        "lieu": f"{commune.nom_departement or '-'} ({str(commune.code_departement).zfill(5) or '-'})",
                        "region": commune.nom_region or "-"
                    })

        # Rendu du template avec les favoris triés
        return render_template(
            "pages/liste_favoris.html",
            sous_titre="Liste des Favoris",
            favoris_festivals=favoris_festivals,
            favoris_monuments=favoris_monuments,
            favoris_communes=favoris_communes,
            form_ajout_favori=form_ajout_favori
        )
    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur dans la route liste_favoris : {str(e)}", exc_info=True)
        flash(f"Une erreur s'est produite : {str(e)}", "error")
        return redirect(url_for("liste_favoris"))

# Route pour supprimer un favori
@app.route("/festivalchezmoi/suppression/favori", methods=['POST'])
@login_required
def suppression_favori():
    try:
        # Récupération des données du formulaire
        nom = request.form.get("nom")
        type_favori = request.form.get("type")
        user_id = current_user.id

        # Vérification du type de favori et récupération de l'entrée correspondante
        if type_favori == "festival":
            favori = db.session.query(relation_user_favori).join(Festival).filter(
                relation_user_favori.c.user_id == user_id,
                Festival.nom_festival == nom
            ).first()
        elif type_favori == "monument":
            favori = db.session.query(relation_user_favori).join(MonumentHistorique).filter(
                relation_user_favori.c.user_id == user_id,
                MonumentHistorique.titre_editorial_de_la_notice == nom
            ).first()
        elif type_favori == "commune":
            favori = db.session.query(relation_user_favori).join(Commune).filter(
                relation_user_favori.c.user_id == user_id,
                Commune.nom_commune == nom
            ).first()
        else:
            flash("Type de favori invalide.", "error")
            return redirect(url_for("liste_favoris"))

        # Suppression du favori s'il existe
        if favori:
            delete_stmt = relation_user_favori.delete().where(
                relation_user_favori.c.user_id == user_id,
                relation_user_favori.c.id_festival == favori.id_festival if type_favori == "festival" else True,
                relation_user_favori.c.id_monument_historique == favori.id_monument_historique if type_favori == "monument" else True,
                relation_user_favori.c.id_commune == favori.id_commune if type_favori == "commune" else True
            )
            db.session.execute(delete_stmt)
            db.session.commit()
            flash(f"Le favori '{nom}' a été supprimé avec succès.", "success")
        else:
            flash(f"Aucun favori trouvé pour '{nom}'.", "error")

    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur lors de la suppression du favori : {str(e)}", exc_info=True)
        db.session.rollback()
        flash(f"Une erreur s'est produite lors de la suppression : {str(e)}", "error")

    # Redirection vers la liste des favoris
    return redirect(url_for("liste_favoris"))

# Route pour l'autocomplétion des favoris
@app.route("/festivalchezmoi/autocomplete", methods=["GET"])
def autocomplete():
    try:
        # Récupération des paramètres de la requête
        query = request.args.get("q", "").lower()
        type_favori = request.args.get("type", "festival")
        results = []

        # Recherche des résultats correspondant au type et à la requête
        if query:
            if type_favori == "festival":
                results = db.session.query(Festival.nom_festival).filter(
                    func.lower(Festival.nom_festival).like(f"%{query}%")
                ).order_by(
                    func.lower(Festival.nom_festival).like(f"{query}%").desc(),
                    Festival.nom_festival.asc()
                ).limit(20).all()
            elif type_favori == "monument":
                results = db.session.query(MonumentHistorique.titre_editorial_de_la_notice).filter(
                    func.lower(MonumentHistorique.titre_editorial_de_la_notice).like(f"%{query}%")
                ).order_by(
                    func.lower(MonumentHistorique.titre_editorial_de_la_notice).like(f"{query}%").desc(),
                    MonumentHistorique.titre_editorial_de_la_notice.asc()
                ).limit(20).all()
            elif type_favori == "commune":
                results = db.session.query(Commune.nom_commune).filter(
                    func.lower(Commune.nom_commune).like(f"%{query}%")
                ).order_by(
                    func.lower(Commune.nom_commune).like(f"{query}%").desc(),
                    Commune.nom_commune.asc()
                ).limit(20).all()

        # Transformation des résultats en une liste de chaînes
        results = [r[0] for r in results]
        return {"results": results}, 200
    except Exception as e:
        # Gestion des erreurs
        app.logger.error(f"Erreur dans /autocomplete : {str(e)}", exc_info=True)
        return {"error": str(e)}, 500
