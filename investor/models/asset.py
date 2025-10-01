from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Asset(models.Model):
    _name = 'investor.asset'
    _description = 'Актив'

    name = fields.Char(string="Наименование", required=True)
    ticker = fields.Char(string="Тикер", required=True)
    asset_type = fields.Selection([
        ('stock', 'Акция'),
        ('bond', 'Облигация'),
        ('currency', 'Валюта'),
        ('fund', 'Фонд')
    ], string="Тип Актива", required=True)
    currency = fields.Selection([
        ('RUB', 'RUB'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('CNY', 'CNY')
    ], string="Валюта Номинала", required=True, default='RUB')
    unit_price = fields.Float(string="Цена за Единицу", digits='Product Price', required=True)

    @api.constrains('ticker')
    def _check_ticker(self):
        for record in self:
            if len(record.ticker) < 3 or not record.ticker.isupper():
                raise ValidationError("Тикер должен содержать 3 или более символов в верхнем регистре.")

class AccountAsset(models.Model):
    _name = 'investor.account.asset'
    _description = 'Актив на Счете'
    _rec_name = 'asset_id'

    account_id = fields.Many2one('investor.account', string="Счет", required=True, ondelete='cascade')
    asset_id = fields.Many2one('investor.asset', string="Актив", required=True, ondelete='cascade')
    quantity = fields.Float(string="Количество", required=True, default=0.0)

    _sql_constraints = [
        ('account_asset_uniq', 'unique (account_id, asset_id)', 'Этот актив уже существует на данном счете.')
    ]
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError("Количество актива не может быть отрицательным.")