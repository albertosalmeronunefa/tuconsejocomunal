# -*- coding: utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class Partner(models.Model):
    _inherit = 'res.partner'
    
    is_council = fields.Boolean(
                    string='Es consejo', 
                    help="Indica sí el partner es un consejo comunal.",
                    )
    
    
class CommunalCouncil(models.Model):
    _name = "tcc.communal.council"
    _description = "Consejo Comunal"
    _inherits = {'res.users': 'user_id'}
    _rec_name = 'name'
    
    
    user_id = fields.Many2one(
                    'res.users', 
                    string='Usuario Consejo Comunal',
                    ondelete="cascade"
                    )
    situr_code = fields.Char(
                    string='Código SITUR',
                    )
    creation_date = fields.Date(
                    string='Fecha creación',
                    )
    rif = fields.Char(
                    string='RIF',
                    )
    state_id = fields.Many2one(
                    'res.country.state', 
                    string='Estado',
                    )
    #~ municipality_id = fields.Many2one(
                    #~ 'res.country.state.municipality', 
                    #~ string='Municipio',
                    #~ )
    #~ parish_id = fields.Many2one(
                    #~ 'res.country.state.municipality.parish', 
                    #~ string='Parroquia',
                    #~ )
    sector_id = fields.Many2one(
                'tcc.address.sector',
                string='Sector', 
                )
    active = fields.Boolean(default=True)
    
    
    _sql_constraints = [('situr_code_uniq', 'unique (situr_code)', "El Código SITUR ya Existe  !")]
    
    @api.onchange('creation_date')
    def to_validate_date(self):
        warning = {}
        result = {}
        if self.creation_date:
            if cmp(datetime.strptime(self.creation_date, DF).date(), date.today()) == 1:
                warning = {
                    'title': _('Warning!'),
                    'message': _('La fecha seleccionada no debe ser mayor a la fecha de hoy.'),
                }
                self.creation_date = False
                if warning:
                    result['warning'] = warning
            return result
    
    @api.onchange('name')
    def title_string(self):
        if self.name:
            self.name = self.name.title()
    
    @api.onchange('state_id')
    def onchangue_state(self):
        if self.state_id:
            self.municipality_id = False
            self.parish_id = False
            self.sector_id = False
    
    @api.onchange('municipality_id')
    def onchangue_municipality(self):
        if self.municipality_id:
            self.parish_id = False
            self.sector_id = False
    
    #~ @api.model
    #~ def create_default_survey(self):
        #~ self.ensure_one()
        #~ survey = self.env['survey.survey']
        #~ 
        #~ question = self.env['survey.question']
        #~ label = self.env['survey.label']
        #~ survey_data = {
            #~ 'title': 'Paricipación Comunitaria',
            #~ 'auth_required': True,
            #~ 'page_ids': [0, False, {'title': 'Paricipación Comunitaria',}]
        #~ }
        #~ 
        #~ survey.create(survey_data)
        #~ return True
    
        
    @api.model
    def create(self, vals):
        council = super(CommunalCouncil, self).create(vals)
        list_group = []
        group_council = council.env['res.groups'].sudo().search([('name', '=', 'Consejo Comunal')])
        list_group.append(group_council.id)
        group_contact = council.env['res.groups'].sudo().search([('name', '=', 'Creación de contactos')])
        list_group.append(group_contact.id)
        group_employee = council.env['res.groups'].sudo().search([('name', '=', 'Empleado')])
        list_group.append(group_employee.id)
        council.sector_id.sudo().write({'communal_council_id': council.id})
        council.user_id.sudo().write({'is_council': True,'groups_id' : [(6,0,list_group)],'email' : council.user_id.login,'communal_council_id': council.id})
        users = council.env['res.users'].sudo().search([('id', '=', council.user_id.id)])
        #~ users = council.env['res.users'].sudo().search([('id', '=', council.user_id.id)])
        users.sudo().write({'communal_council_id': council.id})
        #~ council.create_default_survey()
        return council
    
