# imports de l'appli à modifier en conséquence
from ..app import app, db
from flask import render_template, request, flash
from ..models.formulaires import AjoutFavori, ModificationFavori, SuppressionFavori
from ..models.database import Favoris, Festival, MonumentHistorique
from ..utils.transformations import  clean_arg
from flask_login import current_user

@app.route("/insertion/favori", methods=['GET', 'POST'])
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
                    nouveau_favori = Favoris(user_id=user_id, festival_id=festival.id_festival)
                else:
                    flash("Festival non trouvé", 'error')
                    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)
            elif type == 'monument':
                monument = MonumentHistorique.query.filter_by(nom_monument=nom).first()
                if monument:
                    nouveau_favori = Favoris(user_id=user_id, monument_id=monument.id_monument_historique)
                else:
                    flash("Monument non trouvé", 'error')
                    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)

            db.session.add(nouveau_favori)
            db.session.commit()

            flash("Le favori a été ajouté avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de l'ajout du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/insertion_favori.html", sous_titre="Ajout Favori", form=form)

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
                    favori = Favoris.query.filter_by(user_id=user_id, festival_id=festival.id_festival).first()
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
                    favori = Favoris.query.filter_by(user_id=user_id, monument_id=monument.id_monument_historique).first()
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
                    favori = Favoris.query.filter_by(user_id=user_id, festival_id=festival.id_festival).first()
                else:
                    flash("Festival non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)
            elif type == 'monument':
                monument = MonumentHistorique.query.filter_by(nom_monument=nom).first()
                if monument:
                    favori = Favoris.query.filter_by(user_id=user_id, monument_id=monument.id_monument_historique).first()
                else:
                    flash("Monument non trouvé", 'error')
                    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)

            if favori:
                db.session.delete(favori)
                db.session.commit()

                flash("Le favori a été supprimé avec succès", 'info')
    
    except Exception as e:
        flash("Une erreur s'est produite lors de la suppression du favori : " + str(e), "error")
        db.session.rollback()
    
    return render_template("pages/suppression_favori.html", sous_titre="Suppression Favori", form=form)