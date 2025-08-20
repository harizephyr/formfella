# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# def create_text_form(filename):
#     # Create a canvas with letter page size
#     c = canvas.Canvas(filename, pagesize=letter)
#     width, height = letter

#     # Title
#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(200, height - 50, "Simple Text Form")

#     # Labels for form fields
#     c.setFont("Helvetica", 12)
#     c.drawString(50, height - 100, "Name:")
#     c.drawString(50, height - 130, "Email:")
#     c.drawString(50, height - 160, "Phone:")
#     c.drawString(50, height - 190, "Address:")
#     c.drawString(50, height - 250, "Comments:")

#     # Just text (not interactive fields, since you said only text)
#     c.drawString(150, height - 100, "________________________")
#     c.drawString(150, height - 130, "________________________")
#     c.drawString(150, height - 160, "________________________")
#     c.drawString(150, height - 190, "________________________")
#     c.drawString(50, height - 270, "__________________________________________")
#     c.drawString(50, height - 290, "__________________________________________")
#     c.drawString(50, height - 310, "__________________________________________")

#     # Save PDF
#     c.save()

# create_text_form("generated_form.pdf")



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_registration_form(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 60, "Registration Form")

    # Labels and lines
    c.setFont("Helvetica", 12)

    y = height - 120
    line_gap = 40

    fields = [
        "Full Name",
        "Date of Birth",
        "Email Address",
        "Phone Number",
        "Street Address",
        "City",
        "State",
        "Zip Code",
        "Country",
    ]

    for field in fields:
        c.drawString(50, y, f"{field}:")
        c.line(180, y - 2, width - 50, y - 2)  # underline
        y -= line_gap

    # Signature section
    c.drawString(50, y - 20, "Signature:")
    c.line(150, y - 22, width - 50, y - 22)

    c.drawString(50, y - 60, "Date:")
    c.line(150, y - 62, width - 50, y - 62)

    # Save
    c.save()

create_registration_form("registration_form.pdf")
