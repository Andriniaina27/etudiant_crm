from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re

class Etudiant(models.Model):
    _name = 'etudiants.etudiant'
    _description = 'Étudiant'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Ajout du suivi

    name = fields.Char(string="Nom Complet", required=True, tracking=True)
    numero_etudiant = fields.Char(string="Numéro Étudiant", required=True, unique=True)
    cin = fields.Char(string="CIN", required=True, tracking=True)
    date_naissance = fields.Date(string="Date de Naissance")
    email = fields.Char(string="Email", required=True)
    telephone = fields.Char(string="Téléphone")
    adresse = fields.Text(string="Adresse")
    
    # Champs académiques
    filiere = fields.Selection([
        ('informatique', 'Informatique'),
        ('gestion', 'Gestion'),
        ('commerce', 'Commerce'),
        ('comptabilite', 'Comptabilité'),
    ], string="Filière", required=True)
    
    niveau = fields.Selection([
        ('licence1', 'Licence 1'),
        ('licence2', 'Licence 2'), 
        ('licence3', 'Licence 3'),
        ('master1', 'Master 1'),
        ('master2', 'Master 2'),
    ], string="Niveau")
    
    projet_pfe = fields.Char(string="Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur Académique")
    
    # Relations
    stage_ids = fields.One2many('etudiants.stage', 'etudiant_id', string="Stages")
    stage_count = fields.Integer(compute='_compute_stage_count', string="Nombre de Stages")
    
    # Statut
    state = fields.Selection([
        ('prospect', 'Prospect'),
        ('inscrit', 'Inscrit'),
        ('en_cours', 'En Cours'),
        ('diplome', 'Diplômé'),
    ], string="Statut", default='prospect')
    
    # Contraintes
    @api.constrains('numero_etudiant')
    def _check_numero_etudiant_unique(self):
        for record in self:
            if self.search([('numero_etudiant', '=', record.numero_etudiant), ('id', '!=', record.id)]):
                raise ValidationError("Le numéro d'étudiant doit être unique !")
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Email invalide !")
    
    # Computed fields
    @api.depends('stage_ids')
    def _compute_stage_count(self):
        for record in self:
            record.stage_count = len(record.stage_ids)
    
    # Actions
    def action_view_stages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Stages de {self.name}',
            'res_model': 'etudiants.stage',
            'view_mode': 'tree,form',
            'domain': [('etudiant_id', '=', self.id)],
            'context': {'default_etudiant_id': self.id},
        }
    

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
    
    # Contrainte de dates
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for record in self:
            if record.date_debut and record.date_fin and record.date_fin < record.date_debut:
                raise ValidationError("La date de fin doit être après la date de début !")

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    etudiant_id = fields.Many2one('etudiants.etudiant', string="Étudiant")
    numero_etudiant = fields.Char(string="Numéro Étudiant")
    projet_pfe = fields.Char(string="Projet PFE")
    tuteur_id = fields.Many2one('res.partner', string="Tuteur Académique")
    
    def action_convertir_en_etudiant(self):
        if not self.etudiant_id:
            etudiant = self.env['etudiants.etudiant'].create({
                'name': self.contact_name or self.partner_id.name or self.name,
                'numero_etudiant': self.numero_etudiant or f"ETU{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}",
                'email': self.email_from,
                'telephone': self.phone,
                'projet_pfe': self.projet_pfe,
                'tuteur_id': self.tuteur_id.id,
                'filiere': 'informatique',
            })
            self.etudiant_id = etudiant.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'etudiants.etudiant',
            'res_id': self.etudiant_id.id,
            'view_mode': 'form',
            'target': 'current',
        }