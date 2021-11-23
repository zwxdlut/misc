EXECUTABLE_NAME = example
OBJS = $(patsubst %.c, %.o, $(wildcard *.c))
CC = gcc
CFLAGS = -c -std=c99 -g -Wall
LDFLAGS = -Wall

all: $(EXECUTABLE_NAME)

$(EXECUTABLE_NAME): $(OBJS)
	$(CC) $(LDFLAGS) $^ -o $@

$(OBJS):%.o:%.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf *.o $(EXECUTABLE_NAME)
	
.PHONY: clean

