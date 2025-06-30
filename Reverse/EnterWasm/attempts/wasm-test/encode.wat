(module
  (type (;0;) (func (param i32)))
  (type (;1;) (func (param i32) (result i32)))
  (func (;0;) (type 0) (param i32)
    i32.const 0
    i32.const 0
    i32.load
    local.get 0
    i32.rotr
    i32.store
    i32.const 4
    i32.const 4
    i32.load
    local.get 0
    i32.rotr
    i32.store)
  (func (;1;) (type 0) (param i32)
    i32.const 0
    i32.const 0
    i32.load
    local.get 0
    i32.xor
    i32.store
    i32.const 4
    i32.const 4
    i32.load
    local.get 0
    i32.xor
    i32.store)
  (func (;2;) (type 0) (param i32)
    i32.const 0
    i32.const 0
    i32.load
    local.get 0
    i32.rotl
    i32.store
    i32.const 4
    i32.const 4
    i32.load
    local.get 0
    i32.rotl
    i32.store)
  (func (;3;) (type 1) (param i32) (result i32)
    (local i32 i32 i32 i32 i32 i32 i32)
    loop  ;; label = @1
      local.get 1
      i32.const 0
      i32.add
      i32.load
      i32.const 255
      i32.and
      local.set 5
      local.get 1
      i32.const 8
      i32.add
      i32.load
      i32.const 255
      i32.and
      local.set 6
      local.get 5
      local.get 6
      i32.xor
      local.set 5
      local.get 1
      i32.const 0
      i32.add
      i32.load
      i32.const -256
      i32.and
      local.set 7
      local.get 1
      local.get 5
      local.get 7
      i32.add
      i32.store
      local.get 5
      i32.const 32
      i32.rem_u
      local.get 5
      i32.const 2
      i32.rem_u
      call_indirect (type 0)
      local.get 1
      i32.const 1
      i32.add
      local.set 1
      local.get 1
      i32.const 8
      i32.lt_s
      br_if 0 (;@1;)
    end
    i32.const 0
    i64.load
    i32.const 16
    i64.load
    i64.eq
    return)
  (table (;0;) 10 funcref)
  (memory (;0;) 1)
  (export "memory" (memory 0))
  (export "check" (func 3))
  (elem (;0;) (i32.const 0) func 0)
  (elem (;1;) (i32.const 1) func 2)
  (data (;0;) (i32.const 8) "\dc\87\dbk|\fdm ")
  (data (;1;) (i32.const 16) ",\e4\0e{w\02\1a]"))
