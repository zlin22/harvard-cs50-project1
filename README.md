# Project 1

Web Programming with Python and JavaScript

## Summary
This project contains a website for users to search for books, find reviews for books left by other users of the site, and Goodreads. It also allows the user to leave their own review.

It allows new users to create accounts, as well as allowing existing users to sign in and sign out, while remembering the user's session. It also requires a user to login to be able to use the above functionalities.

## Function of application.py
This is the main Flask application file. It contains all the routing and the database querying code.

## Function of import.py
This is for the **import** portion of the requirement.

## Function of templates/layout.html
This is the layout page for various other pages

## Function of templates/index.html
This is the home page of the site. It determines if the user is logged in. If yes, then the page displays a link for the user to go to search. If no, the page displays a page for the user to login or register for a new account.

## Function of templates/register.html
This page allows the user to register for a new account.

## Function of templates/register-result.html
This page shows the result of the registration process, whether the registration was successful or not.

## Function of templates/search.html
This page allows the user to search for books and returns the results in a list. The user can click on an item in the list to get details of the book.

## Function of templates/book.html
This page allows the user to
1. see the details of the book
2. submit your own review
3. see the reviews that others on this site have submitted
4. see the review information from Goodreads

## Function of templates/login-failed.html
This page shows if the login was incorrect and tells the user to login again.

## Function of templates/logout-success.html
This page shows if the user successfully logged out.

## Function of templates/submit-review-fail.html
This page shows if the user unsuccessfully submitted a review.

## Function of templates/submit-review-success.html
This page shows if the user successfully submitted a review.
