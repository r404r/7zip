# Q1 evidence-only target. Deliberately do not dump the make database/environment.
.PHONY: q1-inputs
q1-inputs:
	$(info Q1_MAKEFILE_LIST=$(MAKEFILE_LIST))
	$(info Q1_OBJS=$(OBJS))
	$(info Q1_CFLAGS=$(CFLAGS))
	$(info Q1_CXXFLAGS=$(CXXFLAGS))
	$(info Q1_LFLAGS_ALL=$(LFLAGS_ALL))
	$(info Q1_USE_ASM=$(USE_ASM))
	$(info Q1_ST_MODE=$(ST_MODE))
	@:
