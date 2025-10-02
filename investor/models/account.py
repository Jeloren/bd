from odoo import models, fields

class Account(models.Model):
    _name = 'investor.account'
    _description = 'Счет'

    name = fields.Char(string="Номер Счета", required=True, index=True)
    account_type = fields.Selection([
        ('iis', 'ИИС'),
        ('broker', 'Брокерский'),
        ('depository', 'Депозитарный')
    ], string="Тип Счета", required=True)
    open_date = fields.Date(string="Дата Открытия", required=True, default=fields.Date.context_today)
    status = fields.Selection([
        ('active', 'Активен'),
        ('closed', 'Закрыт'),
        ('blocked', 'Заблокирован')
    ], string="Статус", required=True, default='active')
    
    investor_id = fields.Many2one('investor.investor', string="Инвестор", required=True, index=True)
    broker_id = fields.Many2one('investor.broker', string="Брокер", required=True, index=True)
    
    transaction_ids = fields.One2many('investor.transaction', 'account_id', string="Транзакции")
    asset_line_ids = fields.One2many('investor.account.asset', 'account_id', string="Активы на счете")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Номер счета должен быть уникальным.')
    ]