/*************************************************
**************************************************
*	@file		crt.S
*	@author		Dário Dias
*	@email		dsd@cin.ufpe.br		
*	@version	0.20
*	@date		9 July 2016
*	@brief		The ArchC Risc-V functional model.
**************************************************
*************************************************/

//include "encoding.h"

#define STACK_SIZE 524288

//512kB for each core

  .text
  .globl _start
  .equ memory_size, 0x20000000

_start:
  li  x1, 0
  li  x2, 0
  li  x3, 0
  li  x4, 0
  li  x5, 0
  li  x6, 0
  li  x7, 0
  li  x8, 0
  li  x9, 0
  li  x10,0
  li  x11,0
  li  x12,0
  li  x13,0
  li  x14,0
  li  x15,0
  li  x16,0
  li  x17,0
  li  x18,0
  li  x19,0
  li  x20,0
  li  x21,0
  li  x22,0
  li  x23,0
  li  x24,0
  li  x25,0
  li  x26,0
  li  x27,0
  li  x28,0
  li  x29,0
  li  x30,0
  li  x31,0
  
  lui sp,0x500
//  csrr t0,mhartid
//  li t1, STACK_SIZE
//  mul t2,t1,t0
//  sub sp,sp,t2
  jal main
  lui t0, 0x20000
  # jalr t0, 0x0
  ebreak

//_interrupt_handler:
//  jal main
//  ebreak

.bss
.align 8
.skip 4096
kstacktop:

.section .tbss
tls_start: