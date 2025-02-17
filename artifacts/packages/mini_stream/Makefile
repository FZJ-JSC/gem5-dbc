CFLAGS  = -O3
LDFLAGS = -fopenmp
LIBS    = -lm
SUFFIX  =

MACROS =

ifneq ($(MARCH),)
  CFLAGS += -march=$(MARCH)
endif

ifneq ($(M5_PREFIX),)
  MACROS += -DUSEM5OPS
  CFLAGS += -I$(M5_PREFIX)/include -L$(M5_PREFIX)/lib
  LIBS   += -lm5
  SUFFIX  = -m5
endif

ifneq ($(LK_PREFIX),)
  MACROS += -DLIKWID_PERFMON
  CFLAGS += -I$(LK_PREFIX)/include -L$(LK_PREFIX)/lib
  LIBS   += -llikwid
  SUFFIX  = -lk
endif

MACROS += -D__COMPILE_COMMAND__="\"$(CC) $(CFLAGS) $(LDFLAGS) $(LIBS)\""

TARGETS = mini_triad$(SUFFIX).x

.PHONY: clean

all: $(TARGETS)

%$(SUFFIX).x: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) $(MACROS) $< $(LIBS) -o $@

clean:
	rm -f *.o *.x
