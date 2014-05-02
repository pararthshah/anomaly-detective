run_hmm <- function(path_str, n_states) {
	n_states
	sc <- read.table(path_str, header= F, sep= "\t")
	ResHMM <- HMMFit(sc[, 2], nStates= n_states)
	Vit <- viterbi(ResHMM, sc[, 2])
	Vit[[1]]
}
