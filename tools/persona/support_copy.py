"""The store's help pages in one voice: the FAQ, the contact page's questions, the refund policy and the shipping
policy say the same thing about the same four products, and nothing the product pages do not.

The export's pages came from the store this one was rebuilt from: a "viral Color-Adapting Foundation" with glycerin,
mica and vitamin E, "clinical study" and "independent panel" percentages, 16-hour wear, "vegan" (the foundation and
the balm carry salmon-derived PDRN, the balm and the serum collagen), a 15% restocking fee beside a "full refund, no
questions asked" guarantee, and three different sets of delivery times. apply_persona.support_pages() writes these
in their place. Facts used here, and where they come from:
- the formula: the product pages (ccf_copy, apf_copy): one adaptive shade that goes on white; hyaluronic acid,
  ceramide NP, squalane, panthenol; peptides (Matrixyl 3000), PDRN, Pro-Xylane; soft-focus powders; fragrance-free;
  no SPF; comfortable through a full day
- the numbers: the product page's 12-week customer survey of women aged 35-65 (self-reported, not a clinical study)
- shipping: one free shipping method for every country (the NEXT store's only method, $0.00); processing and
  delivery times are the store's own shipping table (the shipping policy's), standard shipping only
- returns: the 30-day money-back guarantee every product page states
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import company

E = company.EMAIL
MAIL = f'<a href="mailto:{E}">{E}</a>'
PROCESSING = '1 business day'
DELIVERY = [('United States', '2–4 business days'),
            ('United Kingdom, Canada, Australia, New Zealand and the rest of the EU', '6–9 business days'),
            ('Netherlands, Belgium, France, Germany, Austria and Luxembourg', '6–8 business days'),
            ('Rest of the world', '8–12 business days')]
PRODUCTS = 'the Adaptive Peptide Foundation, the EGF + NAD+ Firming Serum, the PDRN Plumping Balm and The Lymphatic Brush'


def delivery_list():
    return '<ul>' + ''.join(f'<li><strong>{html.escape(w)}:</strong> {d}</li>' for w, d in DELIVERY) + '</ul>'


# the same terms in a product page's "Shipping and returns" tab and its FAQ answers (plain text, no links)
SHIPPING_SHORT = (f'We process orders within {PROCESSING} and ship them free, with tracking. Standard delivery after that: '
                  'United States 2–4 business days; the UK, Canada, Australia, New Zealand and the EU 6–9; the rest of '
                  'the world 8–12.')
RETURNS_SHORT = (f'Try it for 30 days from the day it arrives. If you don’t love it, email {E} with your order number and '
                 'we’ll refund the product’s price in full, even if you’ve opened and used it.')
SHIPPING_TAB_HTML = (f'<p><strong>Processing and delivery</strong><br/>{html.escape(SHIPPING_SHORT, quote=False)}</p>'
                     f'<p><strong>Returns</strong><br/>{html.escape(RETURNS_SHORT, quote=False)}</p>')

GUARANTEE = (f'Try any SKINOFAB product for 30 days from the day it arrives. If you don’t love it, email {MAIL} with your '
             'order number within those 30 days and we’ll refund the product’s price in full, even if you’ve opened '
             'and used it. There is no restocking fee.')

# FAQ page: (the start of the export's question, the question to show or None to keep it, the answer HTML or None to
# drop the question). Matched against the question as the page shows it after the copy rules.
FAQ = [
    ('What is Skinofab', 'What is SKINOFAB?',
     '<p>SKINOFAB makes four products for skin after 45: three formulas made in Korea, the Adaptive Peptide Foundation, '
     'the EGF + NAD+ Firming Serum and the PDRN Plumping Balm, and The Lymphatic Brush.</p>'),
    ('How do I contact Skinofab', 'How do I contact SKINOFAB?',
     f'<p>Email us at {MAIL}, or use the form on our <a href="contact.html">Contact page</a>. We answer every message.</p>'),
    ('How does the', 'How does the Adaptive Peptide Foundation work?',
     '<p>It goes on white. As you blend, its color-adapting pigments release and mix into your skin tone in about a '
     'minute, so there is no shade to choose. The base is a serum: hyaluronic acid, ceramide NP, squalane and panthenol '
     'keep dry skin comfortable; peptides (Matrixyl 3000), PDRN and Pro-Xylane are there for the skin underneath; '
     'soft-focus powders blur the look of lines and pores.</p>'),
    ('What skin tones', 'What skin tones does the foundation work for?',
     f'<p>There is one shade. It goes on white and adapts to your skin tone as you blend. If your skin is very fair or '
     f'deep, email us first at {MAIL} and we’ll tell you honestly how it is likely to look on you. Either way you have '
     f'30 days: if you don’t love how it looks, we’ll refund you.</p>'),
    ('Is Skinofab cruelty-free and vegan', 'Are SKINOFAB products vegan?',
     '<p>No. The PDRN in the Adaptive Peptide Foundation and the PDRN Plumping Balm comes from salmon DNA, and the balm '
     'and the EGF + NAD+ Firming Serum contain collagen.</p>'),
    ('What are the key ingredients', 'What are the key ingredients in the Adaptive Peptide Foundation?',
     '<ul><li><strong>Peptides (Matrixyl 3000), PDRN and Pro-Xylane</strong>: K-beauty actives for the skin underneath.</li>'
     '<li><strong>Hyaluronic acid, ceramide NP, squalane and panthenol</strong>: a hydrating serum base for dry, mature '
     'skin.</li><li><strong>Color-adapting pigments</strong>: they go on white and shift to your tone as you blend.</li>'
     '<li><strong>Soft-focus powders</strong> (silica, boron nitride): they blur the look of lines and pores.</li></ul>'
     '<p>It is fragrance-free and has no SPF. The full ingredient list is on the box.</p>'),
    ('How long does the', 'How long does the foundation last on my skin?',
     '<p>It’s made to stay even and comfortable through a full day, without turning orange or drying into your lines. '
     'If you’re out from morning to dinner, a light touch-up on the nose and chin is usually all it needs.</p>'),
    ('Can I use the foundation with other skincare', None,
     '<p>Yes. Apply your usual moisturizer and your daily sunscreen first, then the foundation. No primer is needed. '
     'You can add concealer or a little powder on top.</p>'),
    ('Where do you ship', None,
     '<p>Everywhere offered at checkout. If your country is in the list there, we ship to it, free.</p>'),
    ('How long does shipping take', None,
     f'<p>We process orders within {PROCESSING}. Standard delivery after that:</p>{delivery_list()}'
     '<p>Weather, customs or carrier delays can add a few days.</p>'),
    ('Do you offer free shipping', None, '<p>Yes. Shipping is free on every order.</p>'),
    ('What is your return policy', None,
     f'<p>{GUARANTEE}</p><p>Unopened products can also be returned within 30 days of delivery for a refund, store '
     'credit or an exchange. See our <a href="../policies/refund-policy.html">refund policy</a>.</p>'),
    ('How do I return a product', None,
     f'<p>Email {MAIL} with your order number and what you’d like: a refund, store credit or an exchange. We reply with '
     'what to do next.</p>'),
    # the export's answer: "products of equal value", the customer pays any difference: the refund policy's terms instead
    ('Do you offer exchanges', None,
     f'<p>Yes, for an unopened product, within 30 days of delivery: email {MAIL} with your order number and the SKINOFAB '
     'product you would like instead. If it costs more or less, we charge or refund the difference. As with any '
     'unopened return, you pay the return shipping, unless we sent the wrong item or it arrived damaged.</p>'),
    ('When will I receive my refund', None,
     '<p>Once your refund is approved we send it to your original payment method straight away. Your bank or card '
     'provider usually shows it within 5 to 10 business days.</p>'),
    ('How long until I see results', None,
     '<p>The color adapts as you blend, in about a minute, and the soft-focus finish shows at once. In a 12-week '
     'customer survey of women aged 35 to 65, 83% said their fine lines looked reduced and 87% saw fewer facial '
     'imperfections. These are self-reported results from a customer survey, not a clinical study. Individual results '
     'vary.</p>'),
    ('How do I apply the', 'How do I apply the Adaptive Peptide Foundation?',
     '<ol><li><strong>Moisturizer and sunscreen first.</strong> No primer needed.</li>'
     '<li><strong>One pump, five dots:</strong> forehead, both cheeks, nose and chin.</li>'
     '<li><strong>Blend outward</strong> with your fingertips or a brush. The white turns into your tone in about a '
     'minute.</li><li><strong>Add a second thin layer</strong> where you want more coverage.</li></ol>'),
    ('Can I use the products if I have sensitive skin', None,
     '<p>The foundation is fragrance-free, with a hydrating serum base. If your skin is sensitive, test a little behind '
     'your ear or along your jaw for 24 hours before using it on your face.</p>'
     '<p>The foundation and the PDRN Plumping Balm contain salmon-derived DNA (PDRN): if you have a fish allergy, ask '
     'your doctor first.</p>'),
    # the checkout takes cards (no PayPal, Apple Pay or Google Pay there, review 3); the cards are the ones the cart
    # and the footer show (Theme settings > Payment logos)
    ('What payment methods', None,
     '<p>We accept major credit and debit cards: Visa, Mastercard, American Express and Discover. On a phone or '
     'browser that supports them, the checkout also offers Apple Pay and Google Pay. Your card details go straight '
     'to our payment processor over an encrypted connection.</p>'),
]

# the contact page's questions: (the start of the question, the question or None to keep it, the answer HTML or None
# to drop it: the Buy 1, Get 1 promotion and the two-month warranty were the old store's)
CONTACT = [
    ('Where do you ship', None, '<p>Everywhere offered at checkout, free. See our <a href="../policies/shipping-policy.html">shipping policy</a>.</p>'),
    ('How long does it take', None,
     f'<p>We process orders within {PROCESSING}. Standard delivery after that:</p>{delivery_list()}'),
    ('Do you offer warranty', None, None),
    ('Can I return my order', None, f'<p>{GUARANTEE}</p>'),
    ('Do you offer refunds', None,
     '<p>Yes, in full, under our 30-day money-back guarantee. See our <a href="../policies/refund-policy.html">refund policy</a>.</p>'),
    ('Why did I only receive 1 item', None, None),
]

REFUND = f"""<p>Every SKINOFAB product comes with a 30-day money-back guarantee.</p>
<h3>30-day money-back guarantee</h3>
<p>{GUARANTEE}</p>
<h3>Unopened products</h3>
<p>You can return an unopened product within 30 days of delivery for a refund, store credit or an exchange. Email {MAIL}
with your order number. For an unopened return you pay the return shipping, unless we sent the wrong item or it
arrived damaged.</p>
<h3>Damaged, defective or wrong items</h3>
<p>If your order arrived damaged, defective or with the wrong item, email {MAIL} with your order number and a photo
within 30 days of delivery. We send a replacement or a full refund, your choice, at no cost to you.</p>
<h3>Exchanges</h3>
<p>You can exchange an unopened product for another SKINOFAB product. If the new product costs more or less, we
charge or refund the difference.</p>
<h3>Automatic Refills</h3>
<p>You can skip or cancel your Automatic Refills at any time before the next refill date by emailing {MAIL}. A refill
that has already shipped is covered by the same 30-day guarantee.</p>
<h3>How refunds are paid</h3>
<p>Refunds go to your original payment method once they are approved. Your bank or card provider usually shows them
within 5 to 10 business days.</p>
<h3>Questions</h3>
<p>{company.LEGAL_NAME}, {company.ADDRESS_LINE}. Email: {MAIL}</p>
"""

SHIPPING = f"""<p>Shipping is free on every order, to every country offered at checkout.</p>
<h3>Processing time</h3>
<p>We process and ship orders within {PROCESSING} of purchase, excluding weekends and holidays. In peak seasons it can
take a little longer.</p>
<h3>Delivery times (standard shipping)</h3>
{delivery_list()}
<p>Weather, customs clearance or carrier delays can add a few days.</p>
<h3>Tracking</h3>
<p>When your order ships we email you its tracking number. You can follow it on our
<a href="../pages/postflows-track-your-order.html">Track your order</a> page.</p>
<h3>Change of address</h3>
<p>To change the address of an order, email {MAIL} as soon as you can. We will do our best, but we can’t change it
once the order has shipped.</p>
<h3>Questions</h3>
<p>{company.LEGAL_NAME}, {company.ADDRESS_LINE}. Email: {MAIL}</p>
"""
