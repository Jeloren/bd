from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

# --------------------------
# ИНВЕСТОР (investor.investor)
# --------------------------
class Investor(models.Model):
    _name = 'investor.investor'
    _description = 'Инвестор'
    
    # Рекомендации по индексам: B-tree для скорости, Trigram для нечеткого поиска
    _sql_constraints = [
        # B-tree: Уникальный индекс для быстрого поиска и обеспечения уникальности
        ('phone_uniq', 'unique (phone)', 'Контактный телефон должен быть уникальным.'),
        ('email_uniq', 'unique (email)', 'Электронная почта должна быть уникальной.')
    ]
    _index = [
        # B-tree: Для сортировки и быстрого поиска
        ('name', 'btree'),
        # Trigram: Для нечеткого поиска по ФИО (например, "Иванов Ив")
        ('name', 'trigram'),
    ]

    # name: required=True (Уже был)
    name = fields.Char(string="ФИО", required=True)
    # birth_date: required=True (Уже был)
    birth_date = fields.Date(string="Дата Рождения", required=True)
    # phone: required=True (Уже был)
    phone = fields.Char(string="Контактный Телефон", required=True)
    # email: Сделать required=True в реальных условиях
    email = fields.Char(string="Электронная Почта", required=True) 
    
    account_ids = fields.One2many('investor.account', 'investor_id', string="Счета")
    broker_ids = fields.Many2many(
        'investor.broker', 
        'investor_broker_rel', 
        'investor_id', 
        'broker_id', 
        string="Брокеры"
    )

    # Валидация
    @api.constrains('email')
    def _check_email_format(self):
        # ... (Код валидации email)
        for record in self:
            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Некорректный формат электронной почты.")

    @api.constrains('birth_date')
    def _check_birth_date(self):
        # ... (Код валидации даты рождения)
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                 raise ValidationError("Дата рождения не может быть в будущем.")

    @api.constrains('phone')
    def _check_phone_format(self):
        # ... (Код валидации телефона)
        for record in self:
            if record.phone and not re.match(r"\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}", record.phone):
                raise ValidationError("Неверный формат телефона. Пример: +7 (999) 123-45-67")


# --------------------------
# СЧЕТ (investor.account)
# --------------------------
class Account(models.Model):
    _name = 'investor.account'
    _description = 'Счет'

    _sql_constraints = [
        # B-tree: Уникальный индекс для номера счета
        ('name_uniq', 'unique (name)', 'Номер счета должен быть уникальным.')
    ]
    # B-tree: Индексы для внешних ключей (частая фильтрация)
    _index = [
        ('investor_id', 'btree'),
        ('broker_id', 'btree'),
        # Составной индекс для поиска счетов инвестора, например, по дате
        ('investor_id, open_date', 'btree'),
    ]
    
    # name: required=True, Уникальный (Уже был)
    name = fields.Char(string="Номер Счета", required=True)
    # ... (Остальные поля)
    account_type = fields.Selection([
        ('iis', 'ИИС'), ('broker', 'Брокерский'), ('depository', 'Депозитарный')
    ], string="Тип Счета", required=True)
    open_date = fields.Date(string="Дата Открытия", required=True, default=fields.Date.context_today)
    status = fields.Selection([
        ('active', 'Активен'), ('closed', 'Закрыт'), ('blocked', 'Заблокирован')
    ], string="Статус", required=True, default='active')
    
    # FK: required=True (Уже был)
    investor_id = fields.Many2one('investor.investor', string="Инвестор", required=True)
    # FK: required=True (Уже был)
    broker_id = fields.Many2one('investor.broker', string="Брокер", required=True)
    # ... (One2many поля)
    transaction_ids = fields.One2many('investor.transaction', 'account_id', string="Транзакции")
    asset_line_ids = fields.One2many('investor.account.asset', 'account_id', string="Активы на счете")


# --------------------------
# АКТИВ (investor.asset)
# --------------------------
class Asset(models.Model):
    _name = 'investor.asset'
    _description = 'Актив'
    
    _sql_constraints = [
        # B-tree: Уникальный индекс для тикера
        ('ticker_uniq', 'unique (ticker)', 'Тикер должен быть уникальным.')
    ]
    _index = [
        # Trigram: Для нечеткого поиска по названию актива
        ('name', 'trigram'),
        # B-tree: Для сортировки и быстрого поиска по тикеру
        ('ticker', 'btree'),
    ]

    # name: required=True (Уже был)
    name = fields.Char(string="Наименование", required=True)
    # ticker: required=True, Уникальный (Уже был)
    ticker = fields.Char(string="Тикер", required=True)
    # ... (Остальные поля)
    asset_type = fields.Selection([
        ('stock', 'Акция'), ('bond', 'Облигация'), ('currency', 'Валюта'), ('fund', 'Фонд')
    ], string="Тип Актива", required=True)
    currency = fields.Selection([
        ('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR'), ('CNY', 'CNY')
    ], string="Валюта Номинала", required=True, default='RUB')
    unit_price = fields.Float(string="Цена за Единицу", digits='Product Price', required=True)

    # ... (Валидация ticker)


# --------------------------
# БРОКЕР (investor.broker)
# --------------------------
class Broker(models.Model):
    _name = 'investor.broker'
    _description = 'Брокер'
    
    _sql_constraints = [
        # B-tree: Уникальный индекс для лицензии
        ('license_number_uniq', 'unique (license_number)', 'Номер лицензии должен быть уникальным.')
    ]
    _index = [
        # Trigram: Для нечеткого поиска по наименованию брокера
        ('name', 'trigram'),
    ]

    # name: required=True (Уже был)
    name = fields.Char(string="Наименование", required=True)
    # license_number: required=True, Уникальный (Уже был)
    license_number = fields.Char(string="Лицензия", required=True)
    # contact_details: Сделать required=True в реальных условиях
    contact_details = fields.Text(string="Контактные Данные", required=True)
    

# --------------------------
# ТРАНЗАКЦИЯ (investor.transaction)
# --------------------------
class Transaction(models.Model):
    _name = 'investor.transaction'
    _description = 'Транзакция'
    _order = 'transaction_datetime desc'

    _index = [
        # B-tree: Критически важные индексы для фильтрации и сортировки
        ('account_id', 'btree'),
        ('asset_id', 'btree'),
        ('transaction_datetime', 'btree'),
        ('operation_type', 'btree'),
    ]

    # ... (compute name)
    
    # transaction_datetime: required=True (Уже был)
    transaction_datetime = fields.Datetime(string="Дата и Время", required=True, default=fields.Datetime.now)
    # operation_type: required=True (Уже был)
    operation_type = fields.Selection([
        ('buy', 'Покупка'), ('sell', 'Продажа'), ('deposit', 'Зачисление'),
        ('withdrawal', 'Списание'), ('commission', 'Комиссия')
    ], string="Тип Операции", required=True)
    # ... (Остальные поля)
    quantity = fields.Float(string="Количество", default=1.0)
    amount = fields.Float(string="Сумма Транзакции", required=True)
    currency = fields.Selection([
        ('RUB', 'RUB'), ('USD', 'USD'), ('EUR', 'EUR')
    ], string="Валюта", required=True, default='RUB')
    
    # account_id: required=True (Уже был)
    account_id = fields.Many2one('investor.account', string="Счет", required=True)
    # asset_id: Рекомендовано сделать обязательным, если транзакция ВСЕГДА связана с активом.
    # Оставляем необязательным, чтобы учесть ввод/вывод денег.
    asset_id = fields.Many2one('investor.asset', string="Актив")
    
    description = fields.Text(string="Дополнительные детали")
    
    # ... (compute display name)

    # Валидация (доработана для реальных условий)
    @api.constrains('quantity', 'amount')
    def _check_positive_values(self):
        for record in self:
            # Количество должно быть положительным при операциях buy/sell
            if record.quantity <= 0 and record.operation_type in ('buy', 'sell'):
                raise ValidationError("Количество должно быть положительным при покупке/продаже.")
            
            # Сумма должна быть больше нуля для всех операций, кроме специфических
            if record.amount <= 0 and record.operation_type in ('buy', 'deposit'):
                 raise ValidationError("Сумма транзакции должна быть положительной для операций покупки или зачисления.")

            # Если транзакция Buy/Sell, Актив должен быть указан
            if record.operation_type in ('buy', 'sell') and not record.asset_id:
                raise ValidationError("Для операций 'Покупка' или 'Продажа' должен быть указан Актив.")

# --------------------------
# СВЯЗЬ СЧЕТ-АКТИВ (investor.account.asset)
# --------------------------
class AccountAsset(models.Model):
    _name = 'investor.account.asset'
    _description = 'Актив на Счете'
    _rec_name = 'asset_id'

    # Составной уникальный индекс для связи (композитный ключ)
    _sql_constraints = [
        # B-tree: Уникальный составной индекс для обеспечения уникальности связи
        ('account_asset_uniq', 'unique (account_id, asset_id)', 'Этот актив уже существует на данном счете.')
    ]
    # B-tree: Индексы для внешних ключей
    _index = [
        ('account_id', 'btree'),
        ('asset_id', 'btree'),
    ]

    # FK: required=True (Уже был)
    account_id = fields.Many2one('investor.account', string="Счет", required=True, ondelete='cascade')
    # FK: required=True (Уже был)
    asset_id = fields.Many2one('investor.asset', string="Актив", required=True, ondelete='cascade')
    # quantity: required=True (Уже был)
    quantity = fields.Float(string="Количество", required=True, default=0.0)

    # ... (Валидация quantity)