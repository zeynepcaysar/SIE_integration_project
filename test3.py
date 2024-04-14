import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")


def parse_email_nlp(email_body):
    doc = nlp(email_body)
    order_date, delivery_date, product_id, quantity = None, None, None, None

    # Example of identifying dates and numbers; customize further as needed
    for ent in doc.ents:
        if ent.label_ == "DATE":
            if not order_date:  # Assuming the first date found is the order date
                order_date = ent.text
            else:
                delivery_date = ent.text
        elif ent.label_ == "CARDINAL" or ent.label_ == "NUMBER":
            if not product_id:  # Assuming the first number could be product ID
                product_id = ent.text
            elif not quantity:  # Assuming the second number could be quantity
                quantity = ent.text

    # Check if all information is gathered
    if all([order_date, delivery_date, product_id, quantity]):
        print("Parsed Order Date:", order_date)
        print("Parsed Delivery Date:", delivery_date)
        print("Parsed Product ID:", product_id)
        print("Parsed Quantity:", quantity)
    else:
        print("NLP could not find all order details.")
        print("Review needed for:", email_body)


# Example email content
email_body = """
- Order Date: April 14, 2024
- Delivery Date: April 20, 2024
- Product ID: 30
- Quantity: 2
"""
parse_email_nlp(email_body)
