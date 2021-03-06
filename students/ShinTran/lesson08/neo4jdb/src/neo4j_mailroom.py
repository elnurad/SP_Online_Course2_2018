'''
Shin Tran
Python 220
Lesson 8 Assignment
'''

#!/usr/bin/env python3
# Implementing the mailroom program using a database connection


from ast import literal_eval
from decimal import Decimal
from pprint import pprint as pp
import logging
import login_database
from neo4j.v1 import GraphDatabase, basic_auth
import sys
import utilities


log = utilities.configure_logger('default', '../logs/mongodb_script.log')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_name_list():
    """Creates a list of all the distinct donors, returns a list
    helper method for print_names"""
    donor_list  = []
    cyph = """MATCH (p:Person) RETURN p.full_name as full_name"""
    result = session.run(cyph)
    for record in result:
        donor_list.append(record['full_name'])
    return list(donor_list)


def print_names():
    """Prints out all the names in the name list,
    references generate_name_list"""
    for name in generate_name_list():
        print(name)


def get_email_text(current_donation):
    """Prints a thank you email to a donator
    Donor name and amount is passed in as a parameter"""
    return "Dear {:s},\n\
        Thank you for the generous donation of ${:,.2f}.\n\
        Sincerely,\n\
        Your Local Charity".format(*current_donation)


def add_donation():
    """Prompts the user to type a name of a donor, enter a donation amount,
    prints an email thanking the donor
    If the user types exit, it would return to the main prompt"""
    temp_list = []
    donor_name = get_donor_name()
    if (donor_name != 'exit'):
        temp_list.append(donor_name)
        donation_amt = get_new_donor_amount()
        if (donation_amt != 'exit'):
            temp_list.append(float(donation_amt))
            logger.info("{} has donated {}".format(*temp_list))
            logger.info("Connecting to DB, to add to the Donor records")
            if donor_name in generate_name_list():
                donor_info = session.run(("""MATCH (p:Person {full_name: '%s'})
                    RETURN p.full_name as full_name, p.donations as donations""") % (donor_name))
                for item in donor_info:
                    dn_list = get_donation_list(item['donations'])
                dn_list.append(temp_list[1])
                session.run("""MATCH (n:Person {full_name: '%s'})
                    SET n.donations = '%s' """ % (donor_name, dn_list))
                print("Database has been updated.")
            else:
                cyph = "CREATE (n:Person {full_name:'%s', donations: '%s'})" % (
                    donor_name, [temp_list[1]])
                session.run(cyph)
            logger.info('Database add successful')
            print(get_email_text(temp_list))


def delete_donor():
    """Prints all the Donor Names, prompts the user to type
    a donation name to delete, removes the Donor node"""
    logger.info("Connecting to DB, to delete a Donor record")
    donor_name = get_donor_name()
    if donor_name in generate_name_list():
        cyph = "MATCH (n:Person {full_name: '%s'}) DELETE n" % (donor_name)
        session.run(cyph)
    logger.info('Database delete successful')


def update_donor():
    """Prompts the user to type a Donor name to update,
    the user to enter a series of donations for the new
    set of donations"""
    logger.info("Connecting to DB, to update a Donor record")
    donor_name = get_donor_name()
    if donor_name in generate_name_list():
        donor_info = session.run(("""MATCH (p:Person {full_name: '%s'})
            RETURN p.full_name as full_name, p.donations as donations""") % (donor_name))
        new_dn_list = []
        new_dn_amt = get_new_donor_amount()
        print("Type 'no' if you want to stop adding donations.")
        while (new_dn_amt != 'no'):
            if float(new_dn_amt) <= 0:
                print("Invald input.")
            else:
               new_dn_list.append(float(new_dn_amt))
            new_dn_amt = get_new_donor_amount()
        if len(new_dn_list) != 0:
            session.run("""MATCH (n:Person {full_name: '%s'})
                    SET n.donations = '%s' """ % (donor_name, new_dn_list))
            logger.info('Database update successful')
    else:
        print("Name not found.")


def send_letters():
    """Goes through all the previous donators, gets their total donated,
    sends a thank you letter that is output on a .txt file"""
    message = "Dear {:s},\n\
    Thank you for donating ${:,.2f}.\n\
    Sincerely,\n\
    Your Local Charity"
    donor_names = session.run("""MATCH (p:Person)
        RETURN p.full_name as full_name, p.donations as donations""")
    for item in donor_names:
        dn_list = get_donation_list(item['donations'])
        with open(item['full_name'] + ".txt",'w') as output:
            output.write(message.format(item['full_name'], sum(dn_list)))
    print("Letters have been generated.")


def generate_report():
    """Generates a report of all the previous donators
    Report includes name, total donated, count of donations, average gift
    Report is also formatted with a certain spacing
    returns the report as a string"""
    donation_total = []
    donor_names = session.run("""MATCH (p:Person)
        RETURN p.full_name as full_name, p.donations as donations""")
    for item in donor_names:
        dn_name = item['full_name']
        dn_list = get_donation_list(item['donations'])
        total_dn = sum(dn_list)
        dn_count = len(dn_list)
        avg_dn = 0
        if dn_count != 0:
            avg_dn = total_dn/dn_count
        donation_total.append([dn_name, total_dn, dn_count, avg_dn])
    donation_total.sort(key=lambda l: l[1], reverse = True)
    s1 = "Donor Name          |   Total Given  |  Num Gifts |  Average Gift\n"
    s2 = "-----------------------------------------------------------------\n"
    final_string = s1 + s2
    for z in range(0, len(donation_total)):
        s3 = '{:20} ${:13,.2f}{:14}  ${:13,.2f}\n'.format(*donation_total[z])
        final_string += s3
    return final_string


def get_donation_list(dn_list):
    """Gets the donations value from the cached dictionary,
    converts it from a string to a list of floats"""
    dn_list = literal_eval(dn_list)
    individual_dns = []
    for i in dn_list:
        individual_dns.append(i)
    return individual_dns


def print_report():
    """Prints a report of all the previous donators references generate_report"""
    print(generate_report())


def get_donor_name():
    """Prompts the user for a donor name"""
    return input("Enter a full name: ")


def get_new_donor_amount():
    """Prompts the user for a donation amount"""
    return input("Enter a donation amount: ")


def clear_db():
    """Clears out the database so it's clean for the next use"""
    sys.exit()
    print("Database has been cleared. Exiting...")
    quit()


def main_prompt():
    """Prompts the user to enter an option"""
    response = input("\n\
        Choose from one of 6 actions:\n\
        1) Add a Donation\n\
        2) Delete a Donor\n\
        3) Update a Donor\n\
        4) Create a Report\n\
        5) Send letters to everyone\n\
        0) Quit\n\
        Please type 1, 2, 3, 4, 5, or 0: ")
    return response


def action(switch_dict):
    """Takes in a user input as a parameter, enters a donation, prints a report,
    prints list, exit, prompts again if the input is bad
    If the user types exit it'll go back to the main prompt"""
    while True:
        user_input = main_prompt()
        try:
            switch_dict.get(user_input)()
        except (TypeError, ValueError):
            print("Invalid input, {} please try again.".format(user_input))


# Python program to use main for function call
if __name__ == "__main__":
    log.info('Step 1: First, clear the entire database, so we can start over')
    log.info("Running clear_all")
    driver = login_database.login_neo4j_cloud()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    log.info("Step 2: Add a few people")
    with driver.session() as session:
        log.info('Adding a few Person nodes')
        log.info('The cyph language is analagous to sql for neo4j')
        for full_name, donations in [
            ('Bom Trady', [500.00, 750.00, 1000.00, 1250.00, 1500.00]),
            ('Raron Aodgers', [1500.00, 2000.00]),
            ('Brew Drees', [2000.00, 3500.00, 5000.00]),
            ('Meyton Panning', [1500.00, 8500.00])]:
            cyph = "CREATE (n:Person {full_name:'%s', donations: '%s'})" % (
                full_name, donations)
            session.run(cyph)
        switch_dict = {
            'list': print_names,
            '1': add_donation,
            '2': delete_donor,
            '3': update_donor,
            '4': print_report,
            '5': send_letters,
            '0': clear_db
        }
        action(switch_dict)
