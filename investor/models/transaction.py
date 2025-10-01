from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Transaction(models.Model):
    _name = 'investor.transaction'
    _description = 'Транзакция'
    _order = 'transaction_datetime desc'

    name = fields.Char(string="Описание", compute='_compute_display_name', store=True)
    transaction_datetime = fields.Datetime(string="Дата и Время", required=True, default=fields.Datetime.now)
    operation_type = fields.Selection([
        ('buy', 'Покупка'),
        ('sell', 'Продажа'),
        ('deposit', 'Зачисление'),
        ('withdrawal', 'Списание'),
        ('commission', 'Комиссия')
    ], string="Тип Операции", required=True)
    quantity = fields.Float(string="Количество", default=1.0)
    amount = fields.Float(string="Сумма Транзакции", required=True)
    currency = fields.Selection([
        ('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')
    ], string="Валюта", required=True, default='RUB')
    
    account_id = fields.Many2one('investor.account', string="Счет", required=True)
    asset_id = fields.Many2one('investor.asset', string="Актив")
    
    description = fields.Text(string="Дополнительные детали")
    
    @api.depends('operation_type', 'asset_id.name', 'account_id.name')
    def _compute_display_name(self):
        for trans in self:
            name_parts = [dict(self._fields['operation_type'].selection).get(trans.operation_type)]
            if trans.asset_id:
                name_parts.append(trans.asset_id.name)
            if trans.account_id:
                name_parts.append(f"({trans.account_id.name})")
            trans.name = " ".join(filter(None, name_parts))

    @api.constrains('quantity', 'amount')
    def _check_positive_values(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Количество должно быть положительным.")
            if record.amount <= 0:
                raise ValidationError("Сумма транзакции должна быть положительной.")