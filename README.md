# Brewers API Documentation

## Table of Contents

- [Summary](#Summary)
- [Route Parameters](#Route-Parameters)
- [Data Modeling](#Data-Modeling)
  - [User](#User-Model)
  - [Drink](#Drink-Model)
  - [Review](#Review-Model)
- [User API](#User-API)
([Single](#Single-User), [Multiple](#Multiple-Users))
- [Drink API](#Drink-API)
([Single](#Single-Drink), [Multiple](#Multiple-Drinks))
- [Review API](#Review-API)
([Single](#Single-Review), [Multiple](#Multiple-Reviews))

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

## Route Parameters

Route parameters are marked by `<type:name>` where `type` is the data type of
the parameter and `name` is the internal name for the parameter. For example,
`/users/<string:email>` can be accessed by `/users/andy@gmail.com`.

## Data Modeling

### User Model

```typescript
class User {
    fname: string,              // first name
    lname: string,              // last name
    email: string,              // email, must be unique
    pw: string,                 // password
    review_ids: Array<string>,  // ObjectIds of review created
    drink_ids: Array<string>,   // ObjectIds of drinks created
    favorite_ids: Array<string> // ObjectIds of drinks favorited
}
```

### Drink Model

```typescript
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

**Returns**: updated `User`.

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

**Returns**: `Array[User]`. If no users are retrieved, returns an empty `Array`.

### POST

**Summary**: Given the necessary data to make a user, creates a User in the
database.

**Parameters**:

- API
  - `<String> fname`: first name
  - `<String> lname`: last name
  - `<String> email`: email, must be unique
  - `<String> pw`: password

**Returns**: newly created `User`.

### DELETE

**Summary**: Given a list of emails, removes the corresponding users from the
database.

**Parameters**:

- API
  - `<Array[String]> emails`: list of users to be deleted by email

**Returns**: `Array[String]` where each element is the email of a deleted user.
If no users are deleted, returns an empty `Array`.

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

**Returns**: updated `Drink`.

### DELETE

**Summary**: Removes the drink and it's reviews from the database. Also detaches
this drink from the user who created it.

**Parameters**:

- Route
  - `<String> _id`: ObjectId of the drink to be deleted.

**Returns**: the `_id` of the removed Drink. `null` if the corresponding
drink DNE.

## Multiple Drinks `/drinks`

### GET

**Summary**: Given a list of drink's ObjectIds, returns a list of the
corresponding drinks.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of drink ObjectIds to be retrieved.

**Returns**: `Array[Drink]`. If no drinks are retrieved, returns an empty
`Array`.

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
of a deleted drink. If no drinks are deleted, returns an empty `Array`.

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

**Returns**: `Array[Review]`. If no drinks are retrieved, returns an empty
`Array`.

### POST

**Summary**: Given the necessary data to make a review, creates a Review in the
database.

**Parameters**:

- API
  - `<String> user_email`: creator's email
  - `<String> drink_id`: ObjectId of the drink this review is for
  - `<String> comment`: comment of the review left
  - `<String> rating`: 1 - 5 rating of the drink

**Returns**: newly created `Drink`.

### DELETE

**Summary**: Given a list of review ObjectIds, removes the corresponding reviews
from the database.

**Parameters**:

- API
  - `<Array[String]> _ids`: list of review ObjectIds to be deleted

**Returns**: `Array[String]` where each element is the ObjectId
of a deleted review. If no reviews are deleted, returns an empty `Array`.
