#-------------------------------------------------------------------------
# AUTHOR: Nhan Thai
# FILENAME: parser.py
# SPECIFICATION: Parse faculty members' name, title, office, phone, email, and website, and persist this data in MongoDB
# FOR: CS 4250- Assignment #3
# TIME SPENT: 3
#-----------------------------------------------------------*/\

# from bs4 import BeautifulSoup
# from pymongo import MongoClient
# import re

# def connectDataBase():

# # Create a database connection object using pymongo
#     DB_HOST = "localhost"
#     DB_PORT = 27017

#     try:
#         client = MongoClient(host=DB_HOST, port=DB_PORT)
#         db = client.corpus
#         return db
    
#     except Exception as e:
#         print("Connect database error: " + str(e))


# def updateDatabase(doc):
#     professor = professors.find_one({"_id": doc["name"]})
#     if (professor):
#         professors.delete_one({"_id": doc["name"]})
#         professors.insert_one(doc)
#     else:
#         professors.insert_one(doc)



# def parser():

#     # use the target page URL to find the Permanent Faculty page in the database
#     url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
#     page = pages.find_one({"_id": url})
#     html = page.get('text')

#     # create beautiful soup object
#     bs = BeautifulSoup(html, 'html.parser')
    
#     # professors info is under text-images section -> clearfix div -> h2 and p
#     # but not all clearfix div have info
#     # get section -> h2 containing name -> div for container
#     section = bs.find('section', {'class':{'text-images'}})
#     headers = section.find_all('h2')
#     containers = []
#     for i in headers:
#         containers.append(i.parent)

# # for each professor
#     for prof in containers:
#         # get name
#         name = prof.h2.get_text().strip()

#         # get title
#         title = prof.find("strong", string=re.compile('(Title){1,1}')).next_sibling.get_text()
#         title = title.strip(": ").strip()

#         # get office
#         office = prof.find("strong", string=re.compile('(Office){1,1}')).next_sibling.get_text()
#         office = office.strip(":").strip()

#         # get email
#         email = prof.find('a', {'href': re.compile("^(mailto:)")}).get('href')
#         email = email.split(":")[1]

#         #get website
#         website = prof.find('a', {'href': re.compile(r"^https?:\/\/www\.cpp\.edu\/faculty")}).get('href')


#         # create professor document
#         doc = {
#             "_id": name,
#             "name": name,
#             "title": title,
#             "office": office,
#             "email": email,
#             "website": website
#         }

#         # update doc in db or insert url if not in db yet
#         updateDatabase(doc)


# db = connectDataBase()
# professors = db.professors
# pages = db.pages
# parser()

# from pymongo import MongoClient
# from bs4 import BeautifulSoup

# # MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['cs4250']
# pages_collection = db['pages']       # Collection containing HTML data
# professors_collection = db['professors']  # New collection for professors' data

# def extract_professor_data(html):
#     """
#     Extract faculty information from the Permanent Faculty HTML page.
#     """
#     soup = BeautifulSoup(html, 'html.parser')
#     professor_data = []

#     # Locate the section containing faculty information
#     faculty_section = soup.find_all('div', class_='faculty-card')  # Adjust if class names differ
#     for faculty in faculty_section:    
#         # Extract data for each professor
#         # Extract the name
#         if faculty.find('h3'):
#             name = faculty.find('h3').get_text(strip=True)
#         else:
#             name = None

#         # Extract the title
#         if faculty.find('p', class_='title'):
#             title = faculty.find('p', class_='title').get_text(strip=True)
#         else:
#             title = None

#         # Extract the office location
#         if faculty.find('p', class_='office'):
#             office = faculty.find('p', class_='office').get_text(strip=True)
#         else:
#             office = None

#         # Extract the phone number
#         if faculty.find('p', class_='phone'):
#             phone = faculty.find('p', class_='phone').get_text(strip=True)
#         else:
#             phone = None

#         # Extract the email address
#         email_tag = faculty.find('a', href=lambda href: href and 'mailto:' in href)
#         if email_tag:
#             email = email_tag.get_text(strip=True)
#         else:
#             email = None

#         # Extract the website URL
#         website_tag = faculty.find('a', href=lambda href: href and not href.startswith('mailto:'))
#         if website_tag:
#             website = website_tag['href']
#         else:
#             website = None


#         # Add the professor's data to the list
#         professor_data.append({
#             'name': name,
#             'title': title,
#             'office': office,
#             'phone': phone,
#             'email': email,
#             'website': website
#         })

#     return professor_data

# def persist_professor_data(professor_data):
#     """
#     Persist professor data into the 'professors' collection in MongoDB.
#     """
#     if professor_data:
#         professors_collection.insert_many(professor_data)
#         print(f"Inserted {len(professor_data)} professors into the database.")
#     else:
#         print("No professor data found to persist.")

# # Main execution
# if __name__ == "__main__":
#     # Locate the Permanent Faculty page in the database
#     target_url = "https://www.cpp.edu/sci/computerscience/faculty-and-staff/permanent-faculty.shtml"
#     page = pages_collection.find_one({'url': target_url})

#     if not page:
#         print("Permanent Faculty page not found in the database.")
#     else:
#         # Extract HTML content from the database
#         html = page['html']

#         # Parse professor data
#         professor_data = extract_professor_data(html)

#         # Persist professor data into MongoDB
#         persist_professor_data(professor_data)

from pymongo import MongoClient
from bs4 import BeautifulSoup

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['cs4250']
pages_collection = db['pages']       # Collection containing HTML data
professors_collection = db['professors']  # New collection for professors' data

def extract_professor_data(html):
    """
    Extract faculty information from the Permanent Faculty HTML page, including handling multiple professors in one block.
    """
    soup = BeautifulSoup(html, 'html.parser')
    professor_data = []

    # Locate all <div class="clearfix"> elements containing faculty info
    faculty_sections = soup.find_all('div', class_='clearfix')
    if not faculty_sections:
        print("[DEBUG] No 'clearfix' sections found. Verify the HTML structure.")
        return []

    print(f"[DEBUG] Found {len(faculty_sections)} faculty entries in the HTML.")

    order = 1  # Initialize order for professors
    for section in faculty_sections:
        # Split content within the same <div> by <hr/>
        segments = section.decode_contents().split('<hr/>')

        for segment_html in segments:
            segment_soup = BeautifulSoup(segment_html, 'html.parser')

            # Extract name from <h2> tags
            name_tag = segment_soup.find('h2')
            name = name_tag.get_text(strip=True) if name_tag else None

            # Skip entries with no name
            if not name:
                print(f"[DEBUG] Skipping entry with missing name at order {order}.")
                order += 1
                continue

            # Initialize details
            title, office, phone, email, website = None, None, None, None, None

            # Extract details from <p> tags
            details = segment_soup.find_all('p')
            for detail in details:
                for strong_tag in detail.find_all('strong'):
                    label = strong_tag.get_text(strip=True).lower()
                    value = (
                        strong_tag.next_sibling.strip()
                        if strong_tag.next_sibling and isinstance(strong_tag.next_sibling, str)
                        else None
                    )

                    if "title" in label:
                        title = value
                    elif "office" in label:
                        office = value
                    elif "phone" in label:
                        phone = value
                    elif "email" in label:
                        email_tag = strong_tag.find_next(
                            'a', href=lambda href: href and 'mailto:' in href
                        )
                        email = email_tag.get_text(strip=True) if email_tag else None
                    elif "web" in label:
                        web_tag = strong_tag.find_next('a', href=True)
                        website = web_tag['href'] if web_tag else None

            # Debugging output for each professor
            print(
                f"[DEBUG] Extracted (Order {order}): Name: {name}, Title: {title}, Office: {office}, Phone: {phone}, Email: {email}, Website: {website}"
            )

            # Add the professor's data to the list
            professor_data.append(
                {
                    'order': order,
                    'name': name,
                    'title': title,
                    'office': office,
                    'phone': phone,
                    'email': email,
                    'website': website,
                }
            )

            order += 1  # Increment order for the next professor

    return professor_data


def persist_professor_data(professor_data):
    """
    Persist professor data into the 'professors' collection in MongoDB.
    """
    if professor_data:
        professors_collection.insert_many(professor_data)
        print(f"[DEBUG] Inserted {len(professor_data)} professors into the 'professors' collection.")
    else:
        print("[DEBUG] No professor data found to persist.")

# Main execution
if __name__ == "__main__":
    # Locate the Permanent Faculty page in the database
    target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
    page = pages_collection.find_one({'url': target_url})

    if not page:
        print("[DEBUG] Permanent Faculty page not found in the database.")
    else:
        # Extract HTML content from the database
        html = page['html']

        # Parse professor data
        professor_data = extract_professor_data(html)

        # Persist professor data into MongoDB
        persist_professor_data(professor_data)





 