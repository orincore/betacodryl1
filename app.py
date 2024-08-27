from flask import Flask, render_template, request, redirect, url_for, flash
from fpdf import FPDF
import os
import re
import datetime

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Function to validate form inputs
def validate_inputs(form_data):
    first_name = form_data.get('first_name', '').strip()
    last_name = form_data.get('last_name', '').strip()
    mobile = form_data.get('mobile_number', '').strip()
    email = form_data.get('email_address', '').strip()
    aadhaar = form_data.get('aadhaar_number', '').strip()
    pan = form_data.get('pan_number', '').strip()

    if not first_name.isalpha() or not last_name.isalpha():
        return "First and Last names should only include characters."
    if not mobile.isdigit():
        return "Mobile number should only contain numerical characters."
    if not re.match(r'\d{4}-\d{4}-\d{4}', aadhaar):
        return "Aadhaar card should be in the format [XXXX-XXXX-XXXX]."
    if not re.match(r'[A-Z]{5}\d{4}[A-Z]', pan):
        return "PAN Number should be in the format [ABCDE1234E]."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Email address is not valid."
    return None

# Function to generate a unique employee ID
def generate_employee_id():
    tracker_file = 'Employee_ID_Tracker.txt'

    # Check if the tracker file exists and has valid content
    if not os.path.exists(tracker_file) or not os.path.getsize(tracker_file):
        last_id = 20000000
    else:
        with open(tracker_file, 'r') as f:
            content = f.read().strip()
            try:
                last_id = int(content)
            except ValueError:
                last_id = 20000000  # Reset to starting value if content is invalid

    new_id = last_id + 1

    # Update the tracker file with the new ID
    with open(tracker_file, 'w') as f:
        f.write(str(new_id))

    return str(new_id)

# Function to generate PDFs for the employer and employee
def generate_pdfs(form_data, employee_id):
    # Combine first name and last name for file and PDF naming
    full_name = f"{form_data['first_name'].strip()} {form_data['last_name'].strip()}"
    folder_name = f"{employee_id}_{full_name.replace(' ', '_')}"

    # Create folders if they don't exist
    emp_folder = os.path.join("Employee", folder_name)
    employer_folder = os.path.join("Employer", folder_name)
    os.makedirs(emp_folder, exist_ok=True)
    os.makedirs(employer_folder, exist_ok=True)

    # Create Offer Letter for Employer
    create_offer_letter_pdf(form_data, employer_folder, employee_id)
    # Create Offer Letter for Employee and Annexures
    create_employee_pdfs(form_data, emp_folder)

    return emp_folder

# Function to create the employer's offer letter PDF
def create_offer_letter_pdf(form_data, folder_path, employee_id):
    pdf = FPDF()
    pdf.add_page()

    # Add logo centered at the top
    pdf.image('static/Frame_26.jpg', x=pdf.w/2-33/2, y=8, w=33)

    # Add company address and offer details
    pdf.set_font("Arial", size=10)  # Set the font size to 10
    pdf.set_xy(10, 40)
    pdf.cell(200, 5, "Codryl Technologies Pvt. Ltd.", ln=True, align='C')
    pdf.cell(200, 5, "Shree Complex, P&T Colony, Dombivli East,", ln=True, align='C')
    pdf.cell(200, 5, "421201, Maharashtra, India", ln=True, align='C')
    pdf.cell(200, 5, f"Date: {datetime.datetime.now().strftime('%d-%b-%Y')}", ln=True, align='C')
    pdf.ln(6)

    # Add employee details
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Mr/Ms. {form_data['first_name'].strip()} {form_data['last_name'].strip()}", ln=True)
    pdf.cell(0, 5, f"{form_data['address_line1'].strip()}, {form_data['street'].strip()}, {form_data['area'].strip()}", ln=True)
    pdf.cell(0, 5, f"{form_data['city'].strip()} - {form_data['zipcode'].strip()}, {form_data['country'].strip()}", ln=True)
    pdf.cell(0, 5, f"Tel# {form_data['mobile_number'].strip()}", ln=True)
    pdf.cell(0, 5, f"Email: {form_data['email_address'].strip()}", ln=True)
    pdf.cell(0, 5, f"Aadhaar Card Number: {form_data['aadhaar_number'].strip()}", ln=True)
    pdf.cell(0, 5, f"PAN Number: {form_data['pan_number'].strip()}", ln=True)
    pdf.cell(0, 5, f"Employee ID: {employee_id}", ln=True)  # Include Employee ID in Employer's PDF
    pdf.ln(6)

    # Subject Line
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "Sub: Offer of Employment", ln=True)
    pdf.ln(6)

    # Generate and add the offer letter content
    generate_offer_letter_content(pdf, form_data)

    # Save the PDF
    pdf_output_path = os.path.join(folder_path, f"{employee_id}_{form_data['first_name'].strip()}_{form_data['last_name'].strip()}.pdf")
    pdf.output(pdf_output_path)

# Function to generate offer letter content
def generate_offer_letter_content(pdf, form_data):
    content = (
        "We are pleased to offer you the position of {designation} at Codryl Technologies Pvt. Ltd. "
        "Your skills and experience are an excellent match for our team, and we look forward to having you join us. "
        "Please find the details of your employment below:\n\n"
        "1. Position:\n"
        "You will be employed as an {designation}. Your responsibilities will include, but are not limited to, "
        "developing and maintaining mobile applications as per the project requirements provided by the company.\n\n"
        "2. Start Date:\n"
        "Your expected start date is {date_of_joining}, subject to successful completion of all pre-employment checks.\n\n"
        "3. Compensation:\n"
        "This position is based on a 'Get Paid as You Work' payment model. You will receive compensation upon the successful "
        "completion of each project assigned to you. The detailed payment structure is provided in Annexure 1.\n\n"
        "4. Work Location:\n"
        "You will be working remotely (Work From Home), with all communication and deliverables to be managed online as per the company's "
        "work-from-home policy detailed in Annexure 2.\n\n"
        "5. Employment Type:\n"
        "This is a contractual position where your employment is tied to the duration of your projects. The company reserves the right to "
        "assign you to various projects as per business needs.\n\n"
        "6. Code of Conduct and Company Policies:\n"
        "You are required to adhere to the rules and regulations of the company, including but not limited to confidentiality, data protection, "
        "and intellectual property rights. Your adherence to company policies is crucial for your continued employment.\n\n"
        "7. Termination:\n"
        "This contract can be terminated by either party with a written notice of [Notice Period] days. The company reserves the right to terminate "
        "employment immediately for any breach of company policies, failure to meet the required performance standards, or violation of any terms "
        "mentioned in the annexures.\n\n"
        "8. Work Schedule:\n"
        "You will have a flexible working schedule, with the requirement to work 8 hours a day for 5 days a week. You may choose any two days as "
        "your week off, provided you inform your manager one week in advance. Mandatory attendance at scheduled meetings is required, and failure "
        "to attend can lead to penalties.\n\n"
        "9. Daily Project Updates:\n"
        "You are required to submit project updates daily on the employee portal. Failure to do so may result in penalties.\n\n"
        "10. Data Security and Client Communication:\n"
        "Data security is of utmost importance. Any breach or leakage of client data will result in immediate termination. Direct communication with clients "
        "without prior approval from your manager is strictly prohibited and will lead to a 180-day suspension.\n\n"
        "11. Absconding and Notice Period:\n"
        "Failure to serve the notice period or absconding from the company will lead to permanent termination from employment at Codryl Technologies Pvt. Ltd.\n\n"
        "12. Post-Project Responsibilities:\n"
        "Upon completion of the project, you are required to submit all the deliverables and transfer all rights to the company. Failure to submit the project "
        "will result in penalties.\n\n"
        "13. Project Submission and Penalties:\n"
        "Delays in project submission will attract penalties. The severity of the penalty will depend on the extent of the delay.\n\n"
        "We are excited to have you as a part of our team. Please review the attached annexures for detailed policies and procedures. If you agree to the terms "
        "and conditions outlined in this offer, please sign and return a copy of this letter along with the annexures.\n\n"
    ).format(
        designation=form_data['designation'].strip(),
        date_of_joining=form_data['date_of_joining']
    )
    
    # Regular content
    pdf.multi_cell(0, 10, content)
    
    # Make the following section bold
    pdf.set_font("Arial", "B", 12)
    
    bold_content = (
        "Sincerely,\n\n"
        "Adarsh Suradkar\n"
        "Devendra Ambre\n"
        "CEO, Founder\n"
        "Codryl Technologies Pvt. Ltd.\n"
        "Authorized Signatory"
    )
    
    pdf.multi_cell(0, 10, bold_content)
    
    # Reset the font back to normal if needed afterward
    pdf.set_font("Arial", "", 12)

# Function to create the employee's offer letter PDF and annexures
def create_employee_pdfs(form_data, folder_path):
    pdf = FPDF()
    pdf.add_page()

    # Add logo centered at the top
    pdf.image('static/Frame_26.jpg', x=pdf.w/2-33/2, y=8, w=33)

    # Add company address and offer details
    pdf.set_font("Arial", size=10)  # Set the font size to 10
    pdf.set_xy(10, 40)
    pdf.cell(200, 5, "Codryl Technologies Pvt. Ltd.", ln=True, align='C')
    pdf.cell(200, 5, "Shree Complex, P&T Colony, Dombivli East,", ln=True, align='C')
    pdf.cell(200, 5, "421201, Maharashtra, India", ln=True, align='C')
    pdf.cell(200, 5, f"Date: {datetime.datetime.now().strftime('%d-%b-%Y')}", ln=True, align='C')
    pdf.ln(6)

    # Add employee details
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"Dear {form_data['first_name'].strip()} {form_data['last_name'].strip()},", ln=True)
    pdf.cell(0, 5, f"Position: {form_data['designation'].strip()}", ln=True)
    pdf.cell(0, 5, f"Date of Joining: {form_data['date_of_joining']}", ln=True)
    pdf.ln(6)

    # Offer letter body
    generate_offer_letter_content(pdf, form_data)

    # Save the PDF
    pdf_output_path = os.path.join(folder_path, "Offer_Letter_Employee.pdf")
    pdf.output(pdf_output_path)

    # Create annexures
    create_annexure_pdfs(folder_path)

# Function to create annexures
def create_annexure_pdfs(folder_path):
    annexures = {
        "Annexure_1_Payment_Structure.pdf": (
            "Annexure 1: Payment Structure\n\n"
            "- Payment for each project will be processed upon successful completion and approval of the deliverables by the client and the company.\n"
            "- Payment will be calculated based on the project scope, complexity, and agreed-upon terms before project initiation.\n"
            "- Any delay in project submission will result in a penalty, deducted from your payment based on the severity of the delay.\n"
            "- All payments will be made in accordance with the completion timelines agreed upon at the start of each project."
        ),
        "Annexure_2_Work_From_Home_Policy.pdf": (
            "Annexure 2: Work From Home Policy\n\n"
            "- You are required to work remotely from your home or any location of your choice, provided that you have a stable internet connection and the necessary tools to complete your tasks.\n"
            "- Regular communication via email, chat, and video conferencing is mandatory.\n"
            "- You must adhere to project deadlines and be available during the core working hours.\n"
            "- All work-related data must be stored securely and in compliance with company policies."
        ),
        "Annexure_3_Payment_Policy.pdf": (
            "Annexure 3: Payment Policy\n\n"
            "- All payments will be processed through bank transfers to the account details provided by you at the time of joining.\n"
            "- You are required to maintain an updated bank account on file with the company to ensure timely payments.\n"
            "- Payment processing time may vary, but typically payments will be made within 5 Days of project completion and approval."
        ),
        "Annexure_4_No_Call_No_Show_Policy.pdf": (
            "Annexure 4: No Call No Show Policy\n\n"
            "- If you fail to respond to company communications for 7 consecutive days without prior notice or approval, it will be considered a 'No Call No Show' violation.\n"
            "- Under this policy, your employment will be terminated immediately, and no further compensation will be provided.\n"
            "- Continuous or repeated violations of this policy may result in permanent disqualification from future employment opportunities with Codryl Technologies Pvt. Ltd."
        )
    }

    for filename, content in annexures.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, content)
        pdf_output_path = os.path.join(folder_path, filename)
        pdf.output(pdf_output_path)

# Main route for the form
@app.route('/')
def index():
    countries = ["United States", "India", "United Kingdom", "Canada", "Australia", "Germany", "France"]
    return render_template('index.html', countries=countries)

# Route to handle form submission and PDF generation
@app.route('/generate', methods=['POST'])
def generate():
    form_data = request.form.to_dict()
    
    # Validate inputs
    error = validate_inputs(form_data)
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    # Generate Employee ID
    employee_id = generate_employee_id()
    
    # Generate PDFs
    emp_folder = generate_pdfs(form_data, employee_id)
    
    # Redirect to success page
    return render_template('success.html', emp_folder=emp_folder)

if __name__ == '__main__':
    app.run(debug=True)
