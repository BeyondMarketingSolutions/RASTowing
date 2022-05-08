import stripe
from static.Services import Services


class PaymentHelper:

    def __init__(self, key):
        stripe.api_key = key

    @staticmethod
    def generate_invoice_link(price, customer, service):
        customer = stripe.Customer.create(
            name=customer.name,
            email=customer.email,
            phone=customer.phone
        )

        product = stripe.Product.search(query=f"active:'true' AND name:'{service}'")["data"][0]

        invoice = stripe.Invoice.create(
            customer=customer.id,
            pending_invoice_items_behavior='exclude',
            collection_method='send_invoice',
            days_until_due=1
        )

        stripe.InvoiceItem.create(
            customer=customer.id,
            invoice=invoice.id,
            description=f'Advance Payment for {service} towards Royal Auto Assistance',
            price_data={
                'currency': 'gbp',
                'unit_amount': price * 100,
                'tax_behavior': 'exclusive',
                'product': product.id
            },
            quantity=1
        )

        payment_link = stripe.Invoice.finalize_invoice(invoice.id)["hosted_invoice_url"]

        stripe.Invoice.send_invoice(invoice.id)

        return payment_link
