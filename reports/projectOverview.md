---
title-block-banner: cropped.jpg
title: Astronomy Database 
date: October 9, 2023
authors: 🌟 Uma Manicka & Celeste Olmstead 🌟
format:
    html:
        theme: cyborg
        toc: false
        embed-resources: true
---



# 🪐Project Overview🪐


See:

* GITHUB REPO:



# Problem Description

Problem domain
: provide summary of the problem domain, providing context, scope of the area. For example, one might talk about the building murals in Richmond, and provide a bit of history (or pictures), so that someone understands the problem domain.

Need
: provide a summary on why a database is needed, and what problem it might help solve. Why does this database need to be developed?

Context, scope and perspective
: Who is the DB for, or what perspective will the DB represent? In the domain of sports teams, is the database for the coach, team owner, player, or fan?

User roles and use cases
: Identify the different user roles that will interact with the database. Describe their needs and how they will use the database. How will the database be used? Who will be using it? How will they be using it? How will the database be connected to other things? 

Security and Privacy
:  Discuss any security and privacy concerns that need to be addressed in the design. Consider user authentication, data encryption, and access controls.

# Database Design

Entity-relationship diagram (ERD)
: Created using proper software tools and consistent notation. Note: your design should consist of at least 4 major entities. You can use Chen notation, Crow’s foot notation, or both; one to show the high-level, logical architecture, and the second to show the more granular data. There will be more than one way to design your database to meet the needs of the problem statement. I’m looking for a discussion of why you make the design choices that you did. Were there any tradeoffs? Did you have to sacrifice one thing for another?

Relational schemas
: Listing of relations, their attributes, types, domain, and constraints, identification of the primary key and foreign keys and other constraints.

Functional Dependencies and Normalization
: A discussion of the functional dependencies in the proposed database schema, and a demonstration of the  normalization of the relations to BCNF/4NF. This might consist of a description, in a text format, of the process of decomposing the tables extracted from the ERD translation into relations satisfying BCNF/4NF. Note that your decomposition via BCNF/4NF must be lossless.

Specific queries
: Given the context, scope, and perspective, the team should pose 20 distinct questions that the database can help answer. These can be general queries of use to all the users, or specific queries for different users or user roles. These questions should be written in precise words and using relational algebra. Leverage Quarto to write the formulas! 10 each

Note: distinct queries are those that are entirely different. Counterexample: "Display a list of student last names in alphabetical order" is not distinct from "Display a list of student names and email addresses". However, "Display a list of student last names in alphabetical order" is distinct from "Who are the five students with the highest GPA?”

Sample Data
: Sample data for each relation your design documented above. I’m looking for 5-10 tuples in each relation, to clearly communicate the domains of each attribute. I suggest that you use chatgpt to help create the tables.  NOTE - results from chatgpt are formatted in markdown, so if you ask chatgpt to produce a table of values with specific columns, you can cut/paste this directly into quarto and get a pretty table!





