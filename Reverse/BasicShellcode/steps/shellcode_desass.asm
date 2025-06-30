
shellcode.bin:     format de fichier binary


Déassemblage de la section .data :

0000000000000000 <.data>:
   0:	41 54                	push   %r12
   2:	41 55                	push   %r13
   4:	41 56                	push   %r14
   6:	48 c7 c0 01 00 00 00 	mov    $0x1,%rax
   d:	4c 8b 14 c7          	mov    (%rdi,%rax,8),%r10
  11:	49 83 fa 20          	cmp    $0x20,%r10
  15:	0f 85 84 00 00 00    	jne    0x9f
  1b:	49 c7 c3 07 00 00 00 	mov    $0x7,%r11
  22:	48 c7 c0 02 00 00 00 	mov    $0x2,%rax
  29:	4c 8b 24 c7          	mov    (%rdi,%rax,8),%r12
  2d:	49 c7 c5 00 00 00 00 	mov    $0x0,%r13
  34:	48 c7 c0 00 00 00 00 	mov    $0x0,%rax
  3b:	4c 8b 34 c7          	mov    (%rdi,%rax,8),%r14
  3f:	4c 89 d8             	mov    %r11,%rax
  42:	49 f7 e5             	mul    %r13
  45:	48 31 d2             	xor    %rdx,%rdx
  48:	49 f7 f2             	div    %r10
  4b:	43 8a 04 2e          	mov    (%r14,%r13,1),%al
  4f:	41 88 04 14          	mov    %al,(%r12,%rdx,1)
  53:	49 83 c5 01          	add    $0x1,%r13
  57:	4d 39 d5             	cmp    %r10,%r13
  5a:	7c e3                	jl     0x3f
  5c:	48 c7 c0 03 00 00 00 	mov    $0x3,%rax
  63:	4c 8b 34 c7          	mov    (%rdi,%rax,8),%r14
  67:	48 c7 c2 01 00 00 00 	mov    $0x1,%rdx
  6e:	49 c7 c3 01 00 00 00 	mov    $0x1,%r11
  75:	4c 89 e7             	mov    %r12,%rdi
  78:	4c 89 de             	mov    %r11,%rsi
  7b:	52                   	push   %rdx
  7c:	41 53                	push   %r11
  7e:	41 ff d6             	call   *%r14
  81:	41 5b                	pop    %r11
  83:	5a                   	pop    %rdx
  84:	48 21 c2             	and    %rax,%rdx
  87:	49 83 c3 01          	add    $0x1,%r11
  8b:	49 83 c4 08          	add    $0x8,%r12
  8f:	49 83 fb 05          	cmp    $0x5,%r11
  93:	7c e0                	jl     0x75
  95:	48 89 d0             	mov    %rdx,%rax
  98:	41 5e                	pop    %r14
  9a:	41 5d                	pop    %r13
  9c:	41 5c                	pop    %r12
  9e:	c3                   	ret
  9f:	48 5c                	rex.W pop %rsp
  a1:	c3                   	ret
  a2:	48 c7 c0 00 00 00 00 	mov    $0x0,%rax
  a9:	41 5e                	pop    %r14
  ab:	41 5d                	pop    %r13
  ad:	41 5c                	pop    %r12
  af:	c3                   	ret
