import uuid

from yookassa import Configuration, Payment

Configuration.account_id = '372377'
Configuration.secret_key = 'test_GweuBNA4H85vWxRCLXLsz7gJLX2lA_YJ2GjYGpRBxLw'


def create_yookassa_payment(summ, base_url):
    return Payment.create({
        "amount": {
            "value": summ,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": base_url + "/appointment/add/success"
        },
        "capture": True,
        "description": "Оплата услуги консультации "
    }, uuid.uuid4())


