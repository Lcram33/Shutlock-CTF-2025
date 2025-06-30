from wasmer import Store, Module, Instance, Function, ImportObject

store = Store()
module = Module(store, open('wasm-test/encode.wasm', 'rb').read())

def debug(x):
    print(f"[DEBUG] {x}")

debug_func = Function(store, debug)
import_object = ImportObject()
import_object.register("js", {"debug": debug_func})

instance = Instance(module, import_object)
memory = instance.exports.memory
check = instance.exports.check

def copy_string_to_memory(s, memory):
    try:
        view = memory.uint8_view()
    except:
        view = memory.int8_view()
    for i, c in enumerate(s):
        view[i] = ord(c)
    return len(s)

def wasm_check(password):
    if len(password) != 8:
        print("La chaîne doit faire 8 caractères.")
        return False
    copy_string_to_memory(password, memory)
    # Appelle check() avec un i32 (par exemple 0, ou l'adresse de la chaîne si besoin)
    result = check(0)  # À adapter selon la signification du paramètre
    return result
