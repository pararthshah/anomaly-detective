require('Rserve')

# get the port from environment (heroku)
# port <- Sys.getenv('PORT')

# run Rserve in process
#Rserve(args="--no-save", debug = FALSE, args = NULL)
Rserve()