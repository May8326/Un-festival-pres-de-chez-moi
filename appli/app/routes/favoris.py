from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.app import app, db
from ..models.database import Festival, MonumentHistorique, Commune, relation_user_favori, LieuFestival
from sqlalchemy import and_, func
from ..models.formulaires import AjoutFavori, ModificationFavori, SuppressionFavori
from ..models.users import Users


@app.route("/festivalchezmoi/insertion/favori", methods=['POST'])
@login_required
def insertion_favori():
    try:
        # Récupérer les données du formulaire
        user_id = current_user.id
        nom_festival = request.form.get("nom_festival")
        nom_monument = request.form.get("nom_monument")
        nom_commune = request.form.get("nom_commune")

        # Initialiser les IDs à None
        festival_id = None
        monument_id = None
        commune_id = None

        # Rechercher le festival si le nom est fourni
        if nom_festival:
            festival = db.session.query(Festival).filter(func.lower(Festival.nom_festival) == nom_festival.lower()).first()
            if festival:
                festival_id = festival.id_festival

        # Rechercher le monument si le nom est fourni
        if nom_monument:
            monument = db.session.query(MonumentHistorique).filter(func.lower(MonumentHistorique.nom_monument) == nom_monument.lower()).first()
            if monument:
                monument_id = monument.id_monument_historique

        # Rechercher la commune si le nom est fourni
        if nom_commune:
            commune = db.session.query(Commune).filter(func.lower(Commune.nom_commune) == nom_commune.lower()).first()
            if commune:
                commune_id = commune.id_commune

        # Vérifier si au moins une information est fournie
        if not (festival_id or monument_id or commune_id):
            flash("Aucune information valide n'a été fournie pour ajouter un favori.", "error")
            return redirect(request.referrer)

        app.logger.info(f"Valeurs insérées : user_id={user_id}, festival_id={festival_id}, monument_id={monument_id}, commune_id={commune_id}")

        # Vérifier si le favori existe déjà
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
            # Ajouter le favori dans la table relation_user_favori
            db.session.execute(
                relation_user_favori.insert().values(
                    user_id=user_id,
                    id_festival=festival_id,
                    id_monument_historique=monument_id,
                    id_commune=commune_id
                )
            )
            db.session.commit()
            flash("Favori ajouté avec succès.", "success")

    except Exception as e:
        app.logger.error(f"Erreur lors de l'ajout du favori : {str(e)}")
        db.session.rollback()
        flash(f"Une erreur s'est produite lors de l'ajout du favori : {str(e)}", "error")

    # Rediriger vers la page précédente
    return redirect(request.referrer)

@app.route("/festivalchezmoi/liste/favoris", methods=['GET', 'POST'])
@login_required
def liste_favoris():
    try:
        app.logger.info(f"Utilisateur connecté : {current_user.id} - {current_user.prenom}")

        # Formulaire pour ajouter un favori
        form_ajout_favori = AjoutFavori()

        if form_ajout_favori.validate_on_submit():
            nom = form_ajout_favori.nom.data
            type_favori = form_ajout_favori.type.data

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

            elif type_favori == 'monument':
                # Utiliser la colonne réelle `titre_editorial_de_la_notice`
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

        # Récupérer les favoris de l'utilisateur connecté
        favoris = db.session.query(relation_user_favori).filter(
            relation_user_favori.c.user_id == current_user.id  # Filtrer par utilisateur actuel
        ).all()
        app.logger.info(f"Favoris récupérés depuis la base de données : {favoris}")

        # Trier les favoris par type
        favoris_festivals = []
        favoris_monuments = []
        favoris_communes = []

        for favori in favoris:
            # Vérification pour les festivals
            if favori.id_festival:
                festival = Festival.query.get(favori.id_festival)
                if festival:
                    app.logger.info(f"Festival trouvé : {festival.nom_festival}")
                    favoris_festivals.append({
                        "nom": festival.nom_festival,
                        "lieu": festival.lieu.commune.nom_commune if festival.lieu and festival.lieu.commune else "N/A",
                        "date": festival.dates.periode_principale_deroulement_festival if festival.dates else "N/A",
                        "contact": festival.contact.site_internet_festival if festival.contact else "N/A"
                    })

            # Vérification pour les monuments
            elif favori.id_monument_historique:
                monument = MonumentHistorique.query.get(favori.id_monument_historique)
                if monument:
                    app.logger.info(f"Monument trouvé : {monument.nom_monument}")
                    favoris_monuments.append({
                        "nom": monument.nom_monument,
                        "lieu": monument.commune.nom_commune if monument.commune else "N/A",
                        "date": monument.dates.datation_edifice if monument.dates else "N/A",
                        "contact": monument.contact.lien_internet_externe if monument.contact else "N/A"
                    })

            # Vérification pour les communes
            elif favori.id_commune:
                commune = Commune.query.get(favori.id_commune)
                if commune:
                    app.logger.info(f"Commune trouvée : {commune.nom_commune}")
                    favoris_communes.append({
                        "nom": commune.nom_commune,
                        "lieu": commune.nom_departement,
                        "date": "N/A",
                        "contact": "N/A"
                    })

        # Log des résultats triés
        app.logger.info(f"Favoris Festivals : {favoris_festivals}")
        app.logger.info(f"Favoris Monuments : {favoris_monuments}")
        app.logger.info(f"Favoris Communes : {favoris_communes}")

        app.logger.info("Rendu du template liste_favoris.html.")
        return render_template(
            "pages/liste_favoris.html",
            sous_titre="Liste des Favoris",
            favoris_festivals=favoris_festivals,
            favoris_monuments=favoris_monuments,
            favoris_communes=favoris_communes,
            form_ajout_favori=form_ajout_favori
        )
    except Exception as e:
        app.logger.error(f"Erreur dans la route liste_favoris : {str(e)}", exc_info=True)
        flash(f"Une erreur s'est produite : {str(e)}", "error")
        return redirect(url_for("accueil_festivalchezmoi"))

@app.route("/festivalchezmoi/suppression/favori", methods=['GET', 'POST'])
@login_required
def suppression_favori():
    form = SuppressionFavori()
    form.type.choices = [('festival', 'Festival'), ('monument', 'Monument')]

    try:
        if form.validate_on_submit():
            user_id = current_user.id
            nom = form.nom.data
            type = form.type.data

            favori = None
            if type == 'festival':
                festival = Festival.query.filter(func.lower(Festival.nom_festival).like(f"%{nom.lower()}%")).first()
                if festival:
                    favori = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_festival == festival.id_festival
                        )
                    ).first()
                else:
                    flash("Festival non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)
            elif type == 'monument':
                monument = MonumentHistorique.query.filter(func.lower(MonumentHistorique.nom_monument).like(f"%{nom.lower()}%")).first()
                if monument:
                    favori = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_monument_historique == monument.id_monument_historique
                        )
                    ).first()
                else:
                    flash("Monument non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)
            elif type == 'commune':
                commune = Commune.query.filter(func.lower(Commune.nom_commune).like(f"%{nom.lower()}%")).first()
                if commune:
                    favori = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_commune == commune.id_commune
                        )
                    ).first()
                else:
                    flash("Commune non trouvée", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)

            if favori:
                # Supprimez l'entrée de la table de relation
                delete_stmt = relation_user_favori.delete().where(
                    and_(
                        relation_user_favori.c.user_id == user_id,
                        relation_user_favori.c.id_commune == commune.id_commune if type == 'commune' else True,
                        relation_user_favori.c.id_festival == festival.id_festival if type == 'festival' else True,
                        relation_user_favori.c.id_monument_historique == monument.id_monument_historique if type == 'monument' else True
                    )
                )
                db.session.execute(delete_stmt)
                db.session.commit()

                flash("Le favori a été supprimé avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de la suppression du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)

@app.route("/festivalchezmoi/debug_favoris")
@login_required
def debug_favoris():
    try:
        # Récupérer les favoris de l'utilisateur connecté
        favoris = db.session.query(relation_user_favori).filter(
            relation_user_favori.c.user_id == current_user.id
        ).all()

        # Préparer les données brutes pour le débogage
        debug_data = []
        for favori in favoris:
            favori_data = {
                "user_id": favori.user_id,
                "id_festival": favori.id_festival,
                "id_monument_historique": favori.id_monument_historique,
                "id_commune": favori.id_commune
            }

            # Ajouter les détails des relations
            if favori.id_festival:
                festival = Festival.query.get(favori.id_festival)
                favori_data["festival"] = {
                    "nom": festival.nom_festival if festival else "Non trouvé",
                    "lieu": festival.lieu.commune.nom_commune if festival and festival.lieu and festival.lieu.commune else "N/A",
                    "date": festival.dates.periode_principale_deroulement_festival if festival and festival.dates else "N/A",
                    "contact": festival.contact.site_internet_festival if festival and festival.contact else "N/A"
                }
            if favori.id_monument_historique:
                monument = MonumentHistorique.query.get(favori.id_monument_historique)
                favori_data["monument"] = {
                    "nom": monument.nom_monument if monument else "Non trouvé",
                    "lieu": monument.commune.nom_commune if monument and monument.commune else "N/A",
                    "date": monument.dates.datation_edifice if monument and monument.dates else "N/A",
                    "contact": monument.contact.lien_internet_externe if monument and monument.contact else "N/A"
                }
            if favori.id_commune:
                commune = Commune.query.get(favori.id_commune)
                favori_data["commune"] = {
                    "nom": commune.nom_commune if commune else "Non trouvé",
                    "departement": commune.nom_departement if commune else "N/A"
                }

            debug_data.append(favori_data)

        # Retourner les données brutes sous forme de JSON
        return {"debug_favoris": debug_data}, 200
    except Exception as e:
        app.logger.error(f"Erreur dans /debug_favoris : {str(e)}", exc_info=True)
        return {"error": str(e)}, 500

@app.route("/festivalchezmoi/test_liste_favoris")
def test_liste_favoris():
    return render_template("pages/liste_favoris.html", favoris_festivals=[], favoris_monuments=[], favoris_communes=[])