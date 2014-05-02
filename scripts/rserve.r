require('Rserve')

# get the port from environment (heroku)
# port <- Sys.getenv('PORT')

# run Rserve in process
Rserve(debug = FALSE, args = NULL)