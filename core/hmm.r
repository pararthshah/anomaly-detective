run_hmm <- function(sc, n_states) {
	#sc <- read.table(path_str, header= F, sep= "\t")
	ResHMM <- HMMFit(sc, nStates= n_states, dis='DISCRETE')
	Vit <- viterbi(ResHMM, sc)
	Vit[[1]]
}
