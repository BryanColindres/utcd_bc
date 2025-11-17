# session_manager.py

# Variables globales de sesión
USUARIO_GLOBAL = 'vacio'
CONTRASENA_GLOBAL = 'None'
ROL_GLOBAL = 'None'

def set_sesion(usuario, contrasena ):
    print(f'hola estoy en se_sesion y el usuario es {usuario} y contraseña {contrasena}')
    """Guarda los datos de sesión globalmente."""
    global USUARIO_GLOBAL, CONTRASENA_GLOBAL 
    USUARIO_GLOBAL = usuario
    CONTRASENA_GLOBAL = contrasena
    print(f'ahora la globales son {USUARIO_GLOBAL}, {CONTRASENA_GLOBAL}')

def get_rol(rol):
    global ROL_GLOBAL
    ROL_GLOBAL = rol
    print(f'hola en el set el rol es {rol}')
    return ROL_GLOBAL

def get_sesion():
    
    """Devuelve una tupla (usuario, contrasena, rol)."""
    print('entre aqui y me estan llamando jejejejejejejejejejejeje')
    print(USUARIO_GLOBAL,CONTRASENA_GLOBAL)
    return USUARIO_GLOBAL, CONTRASENA_GLOBAL, ROL_GLOBAL

def clear_sesion():
    global USUARIO_GLOBAL, CONTRASENA_GLOBAL,ROL_GLOBAL
    USUARIO_GLOBAL = None
    CONTRASENA_GLOBAL = None
    ROL_GLOBAL = None