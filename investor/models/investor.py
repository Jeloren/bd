from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class Investor(models.Model):
    _name = 'investor.investor'
    _description = 'Инвестор'
    _table = 'investor_investor'

    name = fields.Char(string="ФИО", required=True)
    birth_date = fields.Date(string="Дата Рождения", required=True)
    phone = fields.Char(string="Контактный Телефон", required=True)
    email = fields.Char(string="Электронная Почта", required=True)
    
    account_ids = fields.One2many('investor.account', 'investor_id', string="Счета")
    broker_ids = fields.Many2many(
        'investor.broker', 
        'investor_broker_rel', 
        'investor_id', 
        'broker_id', 
        string="Брокеры"
    )
    
    _sql_constraints = [
        ('phone_uniq', 'unique (phone)', 'Контактный телефон должен быть уникальным.'),
        ('email_uniq', 'unique (email)', 'Электронная почта должна быть уникальной.')
    ]
    _index = [
        ('name', 'btree'),
        ('name', 'trigram'),
    ]

    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Некорректный формат электронной почты.")

    @api.constrains('birth_date')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                 raise ValidationError("Дата рождения не может быть в будущем.")

    @api.constrains('phone')
    def _check_phone_format(self):
        for record in self:
            if record.phone and not re.match(r"\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}", record.phone):
                raise ValidationError("Неверный формат телефона. Пример: +7 (999) 123-45-67")