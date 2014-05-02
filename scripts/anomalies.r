detect_SMA <- function(path, window, threshold) {
    sc <- read.table(path, header= F, sep= "\t")
    sc_ma <- SMA(sc,n=window)
}

detect_HMM <- function(path, nstates) {

}