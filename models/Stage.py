from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re


class Stage(models.Model):
    _name = 'etudiants.stage'
    _description = 'Stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Titre du Stage", required=True)
    etudiant_id = fields.Many2one('etudiants.etudiant', string="Étudiant", required=True)
    entreprise_id = fields.Many2one('res.partner', string="Entreprise", required=True)
    date_debut = fields.Date(string="Date de Début", required=True)
    date_fin = fields.Date(string="Date de Fin", required=True)
    description = fields.Text(string="Description")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
    ], string="Statut", default='draft')

    # Contrainte des dates pour bien gerer
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin and record.date_fin < record.date_debut:
                raise ValidationError("La date de fin doit être après la date de début !")
