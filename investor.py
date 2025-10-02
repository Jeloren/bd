from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class Investor(models.Model):
    _name = 'investor.investor'
    _description = 'Инвестор'
    _table = 'investor_investor'

    name = fields.Char(string="ФИО", required=True, index=True)
    birth_date = fields.Date(string="Дата Рождения", required=True)
    phone = fields.Char(string="Контактный Телефон", required=True, index=True)
    email = fields.Char(string="Электронная Почта", required=True, index=True)
    
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
            
            
            
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Asset(models.Model):
    _name = 'investor.asset'
    _description = 'Актив'

    name = fields.Char(string="Наименование", required=True)
    ticker = fields.Char(string="Тикер", required=True, index=True)
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

    account_id = fields.Many2one('investor.account', string="Счет", required=True, ondelete='cascade', index=True)
    asset_id = fields.Many2one('investor.asset', string="Актив", required=True, ondelete='cascade', index=True)
    quantity = fields.Float(string="Количество", required=True, default=0.0)

    _sql_constraints = [
        ('account_asset_uniq', 'unique (account_id, asset_id)', 'Этот актив уже существует на данном счете.')
    ]
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError("Количество актива не может быть отрицательным.")
            
            
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Transaction(models.Model):
    _name = 'investor.transaction'
    _description = 'Транзакция'
    _order = 'transaction_datetime desc'

    name = fields.Char(string="Описание", compute='_compute_display_name', required=True, store=True)
    transaction_datetime = fields.Datetime(string="Дата и Время", required=True, default=fields.Datetime.now, index=True)
    operation_type = fields.Selection([
        ('buy', 'Покупка'),
        ('sell', 'Продажа'),
        ('deposit', 'Зачисление'),
        ('withdrawal', 'Списание'),
        ('commission', 'Комиссия')
    ], string="Тип Операции", required=True)
    quantity = fields.Float(string="Количество", default=1.0, required=True)
    amount = fields.Float(string="Сумма Транзакции", required=True)
    currency = fields.Selection([
        ('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')
    ], string="Валюта", required=True, default='RUB')
    
    account_id = fields.Many2one('investor.account', string="Счет", required=True, index=True)
    asset_id = fields.Many2one('investor.asset', string="Актив", index=True)
    
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
            
            
from odoo import models, fields

class Broker(models.Model):
    _name = 'investor.broker'
    _description = 'Брокер'

    name = fields.Char(string="Наименование", required=True)
    license_number = fields.Char(string="Лицензия", required=True, index=True)
    contact_details = fields.Text(string="Контактные Данные")
    
    
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