from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.app import app, db
from ..models.database import Festival,MonumentHistorique, Commune,relation_user_favori
from sqlalchemy import and_
from ..models.formulaires import AjoutFavori, ModificationFavori, SuppressionFavori
from ..models.users import Users


@app.route("/insertion/favori", methods=['GET', 'POST'])
@login_required
def insertion_favori():
    form = AjoutFavori()
    form.type.choices = [('festival', 'Festival'), ('monument', 'Monument')]

    try:
        if form.validate_on_submit():
            user_id = current_user.id
            nom = form.nom.data
            type = form.type.data

            if type == 'festival':
                festival = Festival.query.filter_by(nom_festival=nom).first()
                if festival:
                    # Vérifier si le festival est déjà dans les favoris
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_festival == festival.id_festival
                        )
                    ).first()
                    if favori_existant:
                            flash("Ce festival est déjà dans vos favoris", 'warning')
                            return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)

                 # Insérer dans la table de relation
                    insert_stmt = relation_user_favori.insert().values(
                        user_id=user_id,
                        id_festival=festival.id_festival,
                        id_monument_historique=None,
                        id_commune=None
                    )
                    db.session.execute(insert_stmt)
                else:
                    flash("Festival non trouvé", 'error')
                    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
        
            # Vérifier si le monument existe et est déjà dans les favoris
            elif type == 'monument':
                monument = MonumentHistorique.query.filter_by(nom_monument=nom).first()
                if monument:
                    # Vérifier si déjà en favori
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_monument_historique == monument.id_monument_historique
                        )
                    ).first()
                    if favori_existant:
                        flash("Ce monument est déjà dans vos favoris", 'warning')
                        return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
                    # Insérer dans la table de relation
                    insert_stmt = relation_user_favori.insert().values(
                        user_id=user_id,
                        id_festival=None,
                        id_monument_historique=monument.id_monument_historique,
                        id_commune=None
                    )
                    db.session.execute(insert_stmt)
                else:
                    flash("Monument non trouvé", 'error')
                    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
            # Vérifier si la commune existe et est déjà dans les favoris
            elif type == 'commune':
                commune = Commune.query.filter_by(nom_commune=nom).first()
                if commune:
                    # Vérifier si déjà en favori
                    favori_existant = db.session.query(relation_user_favori).filter(
                        and_(
                            relation_user_favori.c.user_id == user_id,
                            relation_user_favori.c.id_commune == commune.id_commune
                        )
                    ).first()
                    if favori_existant:
                        flash("Cette commune est déjà dans vos favoris", 'warning')
                        return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
                    # Insérer dans la table de relation
                    insert_stmt = relation_user_favori.insert().values(
                        user_id=user_id,
                        id_festival=None,
                        id_monument_historique=None,
                        id_commune=commune.id_commune
                    )
                    db.session.execute(insert_stmt)
                else:
                    flash("Commune non trouvée", 'error')
                    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
            # Valider la transaction
            db.session.commit()
            # Afficher un message de succès
            flash("Le favori a été ajouté avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de l'ajout du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)

@app.route("/liste/favoris")
def liste_favoris():
    favoris = db.session.query(relation_user_favori).filter(
        relation_user_favori.c.user_id == current_user.id
    ).all()
    return render_template("pages/liste_favoris.html", sous_titre="Liste des Favoris", favoris=favoris)

@app.route("/modification/favori", methods=['GET', 'POST'])
def modification_favori():
    form = ModificationFavori()
    form.type.choices = [('festival', 'Festival'), ('monument', 'Monument')]

    try:
        if form.validate_on_submit():
            user_id = current_user.id
            ancien_nom = form.ancien_nom.data
            nouveau_nom = form.nouveau_nom.data
            type = form.type.data

            favori = None
            if type == 'festival':
                festival = Festival.query.filter_by(nom_festival=ancien_nom).first()
                if festival:
                    favori = db.session.query.filter_by(user_id=user_id, festival_id=festival.id_festival).first()
                    nouveau_festival = Festival.query.filter_by(nom_festival=nouveau_nom).first()
                    if favori and nouveau_festival:
                        favori.festival_id = nouveau_festival.id_festival
                    else:
                        flash("Nouveau festival non trouvé", 'error')
                        return render_template("pages/modification_favori.html", sous_titre="Modification Favori", form=form)
                else:
                    flash("Ancien festival non trouvé", 'error')
                    return render_template("pages/modification_favori.html", sous_titre="Modification Favori", form=form)
            elif type == 'monument':
                monument = MonumentHistorique.query.filter_by(nom_monument=ancien_nom).first()
                if monument:
                    favori = db.session.query.filter_by(user_id=user_id, monument_id=monument.id_monument_historique).first()
                    nouveau_monument = MonumentHistorique.query.filter_by(nom_monument=nouveau_nom).first()
                    if favori and nouveau_monument:
                        favori.monument_id = nouveau_monument.id_monument_historique
                    else:
                        flash("Nouveau monument non trouvé", 'error')
                        return render_template("pages/modification_favori.html", sous_titre="Modification Favori", form=form)
                else:
                    flash("Ancien monument non trouvé", 'error')
                    return render_template("pages/modification_favori.html", sous_titre="Modification Favori", form=form)

            db.session.commit()

            flash("Le favori a été modifié avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de la modification du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/modification_favori.html", sous_titre="Modification Favori", form=form)

@app.route("/suppression/favori", methods=['GET', 'POST'])
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
                festival = Festival.query.filter_by(nom_festival=nom).first()
                if festival:
                    favori = db.query.filter_by(user_id=user_id, festival_id=festival.id_festival).first()
                else:
                    flash("Festival non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)
            elif type == 'monument':
                monument = MonumentHistorique.query.filter_by(nom_monument=nom).first()
                if monument:
                    favori = db.session.query.filter_by(user_id=user_id, monument_id=monument.id_monument_historique).first()
                else:
                    flash("Monument non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)
            elif type == 'commune':
                commune = Commune.query.filter_by(nom_commune=nom).first()
                if commune:
                    favori = db.session.query.filter_by(user_id=user_id, commune_id=commune.id_commune).first()
                else:
                    flash("Commune non trouvée", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)

            if favori:
                db.session.delete(favori)
                db.session.commit()

                flash("Le favori a été supprimé avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de la suppression du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)