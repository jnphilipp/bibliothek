BASH_COMPLETION_DIR=/etc/bash_completion.d/


install: bibliothek.bash-completion
	@install bibliothek.bash-completion $(BASH_COMPLETION_DIR)
