#-------------------------------------------------------------------------
# AUTHOR: Nhan Thai
# FILENAME: parser.py
# SPECIFICATION: Parse faculty members' name, title, office, phone, email, and website, and persist this data in MongoDB
# FOR: CS 4250- Assignment #3
# TIME SPENT: 3
#-----------------------------------------------------------*/\

from pymongo import MongoClient
from bs4 import BeautifulSoup

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['cs4250']
pages_collection = db['pages'] # Collection containing HTML data
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





 
