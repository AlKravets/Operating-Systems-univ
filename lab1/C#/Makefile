all: main.cs
	mcs -out:main.exe main.cs

compile_and_run: main.cs
	mcs -out:main.exe main.cs && mono main.exe

run: main.exe
	mono main.exe