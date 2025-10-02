from odoo import models, fields

class Broker(models.Model):
    _name = 'investor.broker'
    _description = 'Брокер'

    name = fields.Char(string="Наименование", required=True)
    license_number = fields.Char(string="Лицензия", required=True, index=True)
    contact_details = fields.Text(string="Контактные Данные")
    
    _sql_constraints = [
        ('license_number_uniq', 'unique (license_number)', 'Номер лицензии должен быть уникальным.')
    ]