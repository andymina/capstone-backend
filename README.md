# Brewers API Documentation

## Table of Contents

- [Summary](#summary)
- [Error Handling](#error-handling)
- [Route Parameters](#route-parameters)
- [Data Modeling](#data-modeling)
  - [User](#user-model)
  - [Drink](#drink-model)
  - [Review](#review-model)
- [Local Development](#local-development)
- [Authentication](#authentication)
- [User API](#user-api)
([Single](#single-user-usersstringemail), [Multiple](#multiple-users-users))
- [Drink API](#drink-api)
([Single](#single-drink-drinksstring_id), [Multiple](#multiple-drinks-drinks))
- [Review API](#review-api)
([Single](#single-review-reviewsstring_id), [Multiple](#multiple-reviews-reviews))

## Summary

The API is divided into three main sections:

1. User
2. Drink
3. Review

Each of these sections are sub-divided into two further sections: single
instance and multiple instances of each data model. All API routes return an
object where the key `"data"` and the value is what's described in the
route-specified **Returns** section. An example response could be one of the
following:

```javascript
{
    "data": User, Drink, Review, or JSON-compatible data type
}

OR

{
    "data": {
        "item": User, Drink, Review, or JSON-compatible data type
    }
}
```

## Error Handling

If an API endpoint encounters an unexpected error during execution, it will return an error message
within the response. If the API endpoint specifies that `null` will be returned, then it will be
in `res` of the `data` object.

```javascript
{
  "data": {
    "res": as specified by the API endpoint,
    "err": String
  }
}
```

If there validation errors within a form (e.g. poorly formatted email address), an object containing
errors of each field will be returned. The structure is as follows:

```javascript
{
  "data": {
    "email": "Invalid email address",
    "pw": "Password must be between 6 and 18 characters",
    ...
  }
}
```

## Route Parameters

Route parameters are marked by `<type:name>` where `type` is the data type of
the parameter and `name` is the internal name for the parameter. For example,
`/users/<string:email>` can be accessed by `/users/andy@gmail.com`.

## Data Modeling

### User Model

```javascript
class User {
    fname: String,              // first name
    lname: String,              // last name
    email: String,              // email, must be unique
    pw: String,                 // password
    review_ids: Array[String],  // ObjectIds of review created
    drink_ids: Array[String],   // ObjectIds of drinks created
    favorite_ids: Array[String] // ObjectIds of drinks favorited
}
```

### Drink Model

```javascript
class Drink {
    user_email: String,                 // creator's email
    name: String,                       // name of the drink
    review_ids: Array[String],          // ObjectIds of reviews
    ingredients: Array[Array[String]],  // 2D array of ingredients where each
                                        // element is ["type", "unit"]
    rating: Number,                     // overall rating
    sum: Number                         // running sum for avg
}
```

### Review Model

```javascript
class Review {
    user_email: String, // creator's email 
    drink_id: String,   // ObjectId of the drink for this review
    comment: String,    // user's comment
    rating: Number,     // 1 - 5 inclusive rating
    date: String        // ISO 8601 formatted string
}
```

# Local Development

Python version 3.9.7+ is needed to run this back-end locally. The steps are as follows:

1. Clone this repo and `cd` into the root folder of the project.
2. `pip install -r requirements.txt`
3. `python main.py`

# Authentication

Authentication is done through JWTs which expire after 12 hours. To access protected API routes, the
following headers must be included:

```javascript
{
  "Content-Type": "application/json",
  "Authorization": `JWT ${token}` // where token is the token returned from log in or sign up
}
```

## Log in `/users/login`
### POST

**Summary**: Given a user email and pw combination, returns the user in the database.

**Parameters**:

- API
  - `<String> email`: email of the user to be logged in
  - `<String> pw`: password of the user to be logged in

**Returns**: `null` if a user with the given email DNE. If form validation fails, returns the object
described in *Error Handling*. Otherwise, returns a `JWT` and `User` with the following structure.

```
{
  "data": {
    "token": JWT,
    "user": User
  }
}
```

## Sign up `/users`

### POST

**Summary**: Given the necessary data to make a user, creates a User in the database.

**Parameters**:

- API
  - `<String> fname`: first name
  - `<String> lname`: last name
  - `<String> email`: email, must be unique
  - `<String> pw`: password

**Returns**: If form validation fails, returns the object described in
[Error Handling](#error-handling). Otherwise, returns a `JWT` and `User` with the following structure.

```
{
  "data": {
    "token": JWT,
    "user": User
  }
}
```

# User API

## Single User `/users/<string:email>`

### GET

**Summary**: Gets the user with the associated email.

**Parameters**:

- Route
  - `<String> email`: email of the user to be retrieved.

**Returns**: `null` if a user with the given email DNE. Otherwise, `User`.

### PUT

**Summary**: Given an object where the (key, value) pairs are the fields
to be updated, updates the user in the database and returns the updated user.

**Parameters**:

- Route
  - `<String> email`: email of the user to be updated.
- API
  - `<Object> fields`: key represents the property name to updated.
    value represents the new value.

**Returns**: updated `User`. `null` is user with the given email DNE.

### DELETE

**Summary**: Removes the user from the database.

**Parameters**:

- Route
  - `<String> email`: email of the user to be deleted.

**Returns**: the `email` of the removed user. `null` if the corresponding
user DNE.

## Multiple Users `/users`

### GET

**Summary**: Given a list of emails, returns a list of the corresponding users.

**Parameters**:

- API
  - `<Array[String]> emails`: list of emails of users to be retrieved.

**Returns**: `Array[User]`. If a user isn't retrieved, `null` is returned in its place.

### DELETE

**Summary**: Given a list of emails, removes the corresponding users from the
database.

**Parameters**:

- API
  - `<Array[String]> emails`: list of users to be deleted by email

**Returns**: `Array[String]` where each element is the email of a deleted user.
If a user isn't deleted, `null` is returned in its place.

# Drink API

## Single Drink `/drinks/<string:_id>`

### GET

**Summary**: Gets the drink with the associated ObjectId.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the drink to be updated.

**Returns**: `null` if a drink with the given ObjectId DNE. Otherwise, `Drink`.

### PUT

**Summary**: Given an object where the (key, value) pairs are the fields
to be updated, updates the drink in the database and returns the updated drink.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the drink to be updated.
- API
  - `<Object> fields`: key represents the property name to updated.
    value represents the new value.

**Returns**: updated `Drink` if found. `null` if the drink DNE.

### DELETE

**Summary**: Removes the drink and it's reviews from the database. Also detaches
this drink from the user who created it.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the drink to be deleted.
  - `<String> specifier`: Specifies where this drink 

**Returns**: the `_id` of the removed Drink. `null` if the corresponding
drink DNE.

## Multiple Drinks `/drinks`

### GET

**Summary**: Given a list of drink's ObjectIds, returns a list of the
corresponding drinks.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of drink ObjectIds to be retrieved.

**Returns**: `Array[Drink]`. If an `_id` is passed that doesn't correspond to a Drink,
`null` is returned in it's place.

### POST

**Summary**: Given the necessary data to make a drink, creates a Drink in the
database.

**Parameters**:

- API
  - `<String> user_email`: creator's email
  - `<String> name`: name of the drink
  - `<Array[Array[String]]> ingredients`: 2D array of ingredients for this
    drink. See Drink data modeling section for more details.

**Returns**: newly created `Drink`.

### DELETE

**Summary**: Given a list of drink ObjectIds, removes the corresponding drinks
from the database.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of drink ObjectIds to be deleted

**Returns**: `Array[String]` where each element is the ObjectId
of a deleted drink. If a drink isn't deleted, `null` is returned in place of its `_id`.

# Review API

## Single Review `/reviews/<string:_id>`

### GET

**Summary**: Gets the Review with the associated ObjectId.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the review to be retrieved.

**Returns**: `null` if a review with the given ObjectId DNE.
Otherwise, `Review`.

### PUT

**Summary**: Given an object where the (key, value) pairs are the fields
to be updated, updates the review in the database and returns the updated
review.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the review to be updated.
- API
  - `<Object> fields`: key represents the property name to updated.
    value represents the new value.

**Returns**: updated `Review`. If review's rating was updated returns an
`Object` of the following structure:

```javascript
{
    "data": {
        "review": Review,
        "drink_rating": Number
    }
}
```

### DELETE

**Summary**: Removes a review from the database and from it's
associated drink and user.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the review to be deleted.

**Returns**: `null` if no review was deleted. If a review was deleted,
returns `Object` of the following structure:

```javascript
{
    "data": {
        "deleted": String,      // ObjectId of the deleted review
        "drink_rating": Number  // updated rating of the drink
                                // this review was attached to
    }
}
```

## Multiple Reviews `/reviews`

### GET

**Summary**: Given a list of review ObjectIds, returns a list of the
corresponding reviews.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of review ObjectIds to be retrieved.

**Returns**: `Array[Review]`. If a review isn't retrieved, `null` is returned in its place.

### POST

**Summary**: Given the necessary data to make a review, creates a Review in the
database.

**Parameters**:

- API
  - `<String> user_email`: creator's email
  - `<String> drink_id`: ObjectId of the drink this review is for
  - `<String> comment`: comment of the review left
  - `<String> rating`: 1 - 5 rating of the drink

**Returns**: newly created `Review`.

### DELETE

**Summary**: Given a list of review ObjectIds, removes the corresponding reviews
from the database.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of review ObjectIds to be deleted

**Returns**: `Array[String]` where each element is the ObjectId
of a deleted review. If a review isn't deleted, `null` is returned in its place.
