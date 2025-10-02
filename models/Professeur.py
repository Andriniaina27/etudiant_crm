# Fichier: Professeur.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

#class Professeur
class Professeur(models.Model):
    _name = 'etudiants.professeur'
    _description = 'Professeur Académique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom Complet", required=True, tracking=True)
    matricule = fields.Char(string="Matricule", required=True, unique=True, tracking=True)
    cin = fields.Char(string="CIN", tracking=True)
    date_naissance = fields.Date(string="Date de Naissance")
    email = fields.Char(string="Email", required=True)
    telephone = fields.Char(string="Téléphone")
    adresse = fields.Text(string="Adresse")

    # Champs académiques
    departement = fields.Selection([
        ('informatique', 'Informatique'),
        ('gestion', 'Gestion'),
        ('commerce', 'Commerce'),
        ('comptabilite', 'Comptabilité'),
        ('general', 'Général'),
    ], string="Département", required=True)

    # Relations (pour savoir quels étudiants il supervise)
    etudiant_ids = fields.One2many('etudiants.etudiant', 'tuteur_id', string="Étudiants Supervisés")
    etudiant_count = fields.Integer(compute='_compute_etudiant_count', string="Nombre d'Étudiants")

    # Contraintes
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            # Vérification simple de la présence de '@'
            if record.email and '@' not in record.email:
                raise ValidationError("Email invalide pour le professeur !")

    # Computed fields
    @api.depends('etudiant_ids')
    def _compute_etudiant_count(self):
        for record in self:
            record.etudiant_count = len(record.etudiant_ids)

    # Action pour visualiser les étudiants
    def action_view_etudiants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Étudiants de {self.name}',
            'res_model': 'etudiants.etudiant',
            'view_mode': 'tree,form',
            'domain': [('tuteur_id', '=', self.id)],
            'context': {'default_tuteur_id': self.id},
        }