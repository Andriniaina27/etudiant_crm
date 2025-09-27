from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_tuteur = fields.Boolean(string="Est un tuteur académique")
    specialite = fields.Char(string="Spécialité")
    matieres = fields.Text(string="Matières enseignées")
    is_entreprise_accueil = fields.Boolean(string="Entreprise d'accueil")
    secteur_activite = fields.Char(string="Secteur d'activité")