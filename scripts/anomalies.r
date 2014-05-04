detect_SMA <- function(path, window, threshold) {
    sc <- read.table(path, header= F, sep= "\t")
    sc_val <- sc[,2]
    sc_ma <- SMA(sc_val,n=window)
    sc$diff <- abs(sc_ma-sc_val)
    sc_sorted <- sc[with(sc,order("diff","V1")),]
    #sdev <- threshold*sd(sc_diff, na.rm=TRUE)
    return(sc_sorted[:threshold,"V1"])
}

detect_HMM <- function(path, nstates) {

}