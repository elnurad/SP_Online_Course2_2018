#!/usr/bin/env python3
import configparser
from pathlib import Path
import pymongo
import redis
from neo4j.v1 import GraphDatabase, basic_auth
import login_database

import utilities

log = utilities.configure_logger('default', '../logs/login_databases_dev.log')
config_file = Path(__file__).parent.parent / '.config/config'
config = configparser.ConfigParser()


def add_donor(name, amount):
    if name not in get_all_donor_names():
        donors.insert_one({'name': name, 'donations': [amount]})
        print("{} hasn't donated any before. Adding into Donor table.".format(name))
    else:
        print("Found a donor from the database, appending his/her gift amount to the table.")
        donors.update_one(
            {'name': name},
            {'$push': {'donations': amount}}
        )



def get_all_donor_names():
    return [donor['name'] for donor in donors.find()]


def list_all_donor_names_sorted():
    return "\n".join(sorted(get_all_donor_names()))


def send_thank_you():
    donor_name = None
    while not donor_name:
        donor_name = donor_name_prompt()
        if donor_name.lower() == "list":
            print(list_all_donor_names_sorted())
            donor_name = None

    donation = None
    while not donation:
        try:
            donation = donation_prompt()
        except ValueError:
            print("Not a valid number! Please enter a valid number:\n")

    # If the donnor doesn't exist in the donor list - add his info
    # if donor_name not in get_all_donor_names():
    try:
        add_donor(donor_name, donation)
    except ValueError:
        print("Please enter both of your \"First Name\" and \"Last Name\"")
    # else:
    #     for donor in self.donors:
    #         if donor.full_name == donor_name:
    #             donor.add_donation(donation)

    print("Thank You Email:  Thanks for the donation!\n\n")


def group_donations():
    report = []  # initialize report
    for donor in donors.find():
        report.append([donor['name'], sum(donor['donations']), len(donor['donations'])])

    # Sort the report based on donations
    return sorted(report, key=lambda r: r[1], reverse=True)


def create_report():
    print("\nDonor Name           |  Total Given | Num Gifts | Average Gift")
    print("---------------------------------------------------------------\n")

    # Create the report
    for donor_report in group_donations():
        print("{:23}${:12.2f}{:10}   ${:12.2f}".format(donor_report[0],
            donor_report[1],
            donor_report[2],
            donor_report[1] / donor_report[2]))
    print("\n")


def delete_donation():
    delete_name = input("Whose first name do you want to delete from the donation database? \n")

    if delete_name in get_all_donor_names():
        donors.delete_one( 
            {
                'name': {'$eq': delete_name}                    
            }
        )
        print('{} {} has been removed from the database.'.format(donor['first_name'], donor['last_name']))
    else:
        print("Can't find the name you want to delete.")


def quit_program():
	print("Thanks for using my script! Bye!")


def donor_data():
    """
        Sample donor data
    """

    donor_data = [
        {
            'name': 'Bill Gates',
            'donations': [234.22, 45.24, 453.09, 923.01]
        },
        {
            'name': 'Jeff Bezo',
            'donations': [458.21]
        },
        {
            'name': 'Mike Dell',
            'donations': [299.09, 73.67]
        },
        {
            'name': 'Harry Potter',
            'donations': [834.09, 48.04, 34.23]
        }
    ]
    return donor_data


with login_database.login_mongodb_cloud() as client:
    database = client['dev']

    donors = database['donors']
    donors.insert_many(donor_data())

    for donor in donors.find():
        print('Donor Name: {}  {}'.format(donor['name'], donor['donations'])) 

    # database.drop_collection('donors')


# d1 = Donor("Bill", "Gates", [234.22, 45.24, 453.09, 923.01])
# d2 = Donor("Jeff", "Bezo", [464.23])
# d3 = Donor("Mike", "Dell", [299.09, 73.67])
# d4 = Donor("Harry", "Potter", [834.09, 48.04, 34.23])
# d5 = Donor("Ben", "Williams", [83.00, 1334.34])
# d6 = Donor("Guy", "James", [93.00, 34.34])

# db = DonorBook([d1, d2, d3, d4, d5, d6])
# db = DonorBook([])
# new_db =[] # New donor list for storing in Challenge Report

QUIT_OPT = '4'

selection_map = {
    "1": send_thank_you,
    "2": create_report,
    # "3": db.send_letters,
    "3": delete_donation,
    "4": quit_program
    # "5": db.challenge_report,
    # "6": db.projections
}

menu = {
    'op1': "Send a Thank You",
    'op2': "Create a Report",
    # 'op3': "Send Letters To Everyone",
    'op3': "Delete a donation",
    'op4': "Quit"
    # 'op5': "Challenge",
    # 'op6': "Run Projections"
}

def prompt():
    return input("\nPlease choose the following options:\n1) {op1}.\n2) {op2}.\n3)"
        " {op3}.\n4) {op4}.\n".format(**menu))
        # " {op3}.\n4) {op4}.\n5) {op5}.\n6) {op6}.\n".format(**menu))


def donation_prompt():
    return float(input("Please enter the donation amount:\n"))


def donor_name_prompt():
    return input("Send a Thank You - Please enter a full name or type \"list\""
        "to list the current donors:\n")

def challenge_prompt():
    return int(input("What's your challenge factor?\n"))

def min_donation_prompt():
    return int(input("What's minimum donation you want to set? (Default is $1000)\n"))

def main():
    option_value = 0
    while option_value != QUIT_OPT:
        try:
            option_value = prompt()
            selection_map[option_value]()
        except KeyError:
            print("%s is not a valid option! Please try again.\n" % option_value)


# start the script
if __name__ == "__main__":
    main()
