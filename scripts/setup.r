#!/usr/bin/Rscript

usrLibrary <- Sys.getenv("R_LIBS_USER")

if (!require("RHmm")) {
  install.packages('e1071',lib=usrLibrary,repos="http://cran.rstudio.com/",dependencies=TRUE)
}

if (!require("TTR")) {
  install.packages('FSelector',lib=usrLibrary,repos="http://cran.rstudio.com/",dependencies=TRUE)
}