"""
    neo4j example
"""


import utilities
import login_database
import utilities
from random import randint

log = utilities.configure_logger('default', '../logs/neo4j_script.log')


def run_example():

    log.info('Step 1: First, clear the entire database, so we can start over')
    log.info("Running clear_all")

    driver = login_database.login_neo4j_cloud()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    log.info("Step 2: Add a few people")

    with driver.session() as session:

        log.info('Adding a few Person nodes')
        log.info('The cyph language is analagous to sql for neo4j')
        for first, last in [('Bob', 'Jones'),
                            ('Nancy', 'Cooper'),
                            ('Alice', 'Cooper'),
                            ('Fred', 'Barnes'),
                            ('Mary', 'Evans'),
                            ('Marie', 'Curie'),
                            ('Michael', 'Scott'),
                            ('Pamela', 'Beasley'),
                            ('Jim', 'Halpert')
                            ]:
            cyph = "CREATE (n:Person {first_name:'%s', last_name: '%s'})" % (
                first, last)
            session.run(cyph)

        log.info('Adding a few Color nodes')
        for color in ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Indigo', 'Violet']:
            cyph = "CREATE (n:Color {color:'%s'})" % (
                    color)
            session.run(cyph)

        log.info("Step 3a: Get all of people in the DB:")
        cyph = """MATCH (p:Person)
                  RETURN p.first_name as first_name, p.last_name as last_name
                """
        result = session.run(cyph)
        print("People in database:")
        for record in result:
            print(record['first_name'], record['last_name'])

        log.info("Step 3b: Get all the colors in the DB:")
        all_colors = []
        cyph = """MATCH (c:Color)
                  RETURN c.color as color
                """
        result = session.run(cyph)
        print("Colors in database:")
        for record in result:
            print(record['color'])
            all_colors.append(record['color'])

        # log.info('Step 4: Create some relationships')
        # log.info("Bob Jones likes Alice Cooper, Fred Barnes and Marie Curie")
        #
        # for first, last in [("Alice", "Cooper"),
        #                     ("Fred", "Barnes"),
        #                     ("Marie", "Curie")]:
        #     cypher = """
        #       MATCH (p1:Person {first_name:'Bob', last_name:'Jones'})
        #       CREATE (p1)-[friend:FRIEND]->(p2:Person {first_name:'%s', last_name:'%s'})
        #       RETURN p1
        #     """ % (first, last)
        #     session.run(cypher)

        # log.info("Step 5: Find all of Bob's friends")
        # cyph = """
        #   MATCH (bob {first_name:'Bob', last_name:'Jones'})
        #         -[:FRIEND]->(bobFriends)
        #   RETURN bobFriends
        #   """
        # result = session.run(cyph)
        # print("Bob's friends are:")
        # for rec in result:
        #     for friend in rec.values():
        #         print(friend['first_name'], friend['last_name'])

        # log.info("Setting up Marie's friends")

        # for first, last in [("Mary", "Evans"),
        #                     ("Alice", "Cooper"),
        #                     ('Fred', 'Barnes'),
        #                     ]:
        #     cypher = """
        #       MATCH (p1:Person {first_name:'Marie', last_name:'Curie'})
        #       CREATE (p1)-[friend:FRIEND]->(p2:Person {first_name:'%s', last_name:'%s'})
        #       RETURN p1
        #     """ % (first, last)

            # session.run(cypher)

        # print("Step 6: Find all of Marie's friends?")
        # cyph = """
        #   MATCH (marie {first_name:'Marie', last_name:'Curie'})
        #         -[:FRIEND]->(friends)
        #   RETURN friends
        #   """
        # result = session.run(cyph)
        # print("\nMarie's friends are:")
        # for rec in result:
        #     for friend in rec.values():
        #         print(friend['first_name'], friend['last_name'])

        log.info('Step 7: Create their favorite colors')
        cyph = """MATCH (p:Person)
                  RETURN p.first_name as first_name, p.last_name as last_name
                """
        result = session.run(cyph)
        for record in result:
            color_list = all_colors.copy()
            color_array = []
            random_number = randint(1, len(color_list)-1)
            for num in range(0, random_number):
                color_index = randint(0, random_number)
                color_array.append(color_list[color_index])
                del color_list[color_index]
                random_number -= 1
            for color in color_array:
                cypher = """
                  MATCH (p1:Person {first_name:'%s', last_name:'%s'})
                  CREATE (p1)-[f:FAVORITE_COLORS]->(c:Color {color:'%s'})
                  RETURN p1
                """ % (record['first_name'], record['last_name'], color)
                session.run(cypher)

        log.info("Step 8: Get everyone's favorite colors:")
        cyph = """MATCH (p:Person)
                  RETURN p.first_name as first_name, p.last_name as last_name
                """
        result = session.run(cyph)
        for record in result:
            cyph = """
              MATCH (person {first_name:'%s', last_name:'%s'})
                    -[:FAVORITE_COLORS]->(personFavColors)
              RETURN personFavColors
              """ % (record['first_name'], record['last_name'])
            result = session.run(cyph)
            print("{}'s favorite colors are:".format(record['first_name']))
            for rec in result:
                for color in rec.values():
                    print(color['color'])

        log.info("Step 9: Show who has favorited each color:")
        for color in all_colors:
            cyph = """
              MATCH (color {color:'%s'})
                    -[:FAVORITE_COLORS]-(peopleList)
              RETURN peopleList
              """ % color
            result = session.run(cyph)
            print("{} is favorited by:".format(color))
            for rec in result:
                for person in rec.values():
                    print(person['first_name'])
