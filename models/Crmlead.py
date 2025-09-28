from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import re

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