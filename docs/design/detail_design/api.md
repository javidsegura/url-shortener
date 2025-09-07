## API Design 
### High-level description 
- Entities:
  - users
  - og links
  - shortened links
  - firebase profiles
- Relationships:
  - a user has an og link
  - a shortend link comes derived from an og-link
  - each user has a firebase profile
- Actions:
  - a user takes a original link into a shortened version
  - a user can have its firebase profiel modified (image, name, password)
### API endpoints
#### Backend
- /shorten
  - Params: original_link, expires_at
  - Header: token_id 
  - Functionality:
      - Fetches user profile to see settings, then transforms (handle collisions, gives existing linking if duplicate) \
      url, stores actions in db, writes url key to redis with value of og url
 - Errors:
      - 401 Unauthroized
      - 429 Rate-limited
      - 409 alias already exists 
      - 400 url is invalid
- /{url} => collection
  - Params: url_path
  - Header: null
  - Functionality:
      - Retrieves og link from redis based on url_path, then redirects
   - Errors:
      - 4xx
        - URL not found

#### Frontend
- /users/{username} => collection
  - Params:  
  - Header: token_id 
  - Functionality:
      - Shows firebase config (and allows to modify), list of links and if deprecated and click_count
 - Errors:
      - 4xx
        - No permissions
- /register
  - Params:  
  - Header:  
  - Functionality:
      - Registers user in frontend, notifies backend to store data
- /log-in
  - Params:  
  - Header:  
  - Functionality:
      - Sings in the given user
 - Errors:
## RESPONSE SCHEMAS
[See here](https://claude.ai/chat/501237a2-3466-4138-b663-66f571c621bf)