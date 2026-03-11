// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

@R14
A=M
D=M
@minValue
M=D
@maxValue
M=D

@minIndex
M=0
@maxIndex
M=0
@i
M=0
@currentElementValue
M=0

(LOOP)
@i
D=M
@R15
D=D-M
@SWITCH_ELEMENTS
D;JGE

@i
D=M
@R14
A=M+D
D=M
@currentElementValue
M=D

@currentElementValue
D=M
@maxValue
D=D-M
@CHANGE_MAXIMUM
D;JGT

@currentElementValue
D=M
@minValue
D=D-M
@CHANGE_MIN
D;JLT

@i
M=M+1
@LOOP
0;JMP

(CHANGE_MAXIMUM)
@i
D=M
@maxIndex
M=D
@currentElementValue
D=M
@maxValue
M=D
@i
M=M+1
@LOOP
0;JMP

(CHANGE_MIN)
@i
D=M
@minIndex
M=D
@currentElementValue
D=M
@minValue
M=D
@i
M=M+1
@LOOP
0;JMP

(SWITCH_ELEMENTS)
@minIndex
D=M
@R14
A=M+D
D=A
@minAddress
M=D
@maxValue
D=M
@minAddress
A=M
M=D

@maxIndex
D=M
@R14
A=M+D
D=A
@maxAddress
M=D
@minValue
D=M
@maxAddress
A=M
M=D

(END)
@END
0;JMP