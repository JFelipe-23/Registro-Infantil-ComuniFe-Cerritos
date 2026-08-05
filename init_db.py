from models import app, db, SalonCSV

with app.app_context():
    db.create_all()

    if SalonCSV.get_all_admin() == []:
        print("--- CREACIÓN DE SALÓN ADMINISTRADOR ---")
        nombre = input("Nombre: ")
        usuario = input("Usuario: ")

        contrasena = "A"
        contrasena_2 = "B"

        while contrasena != contrasena_2:
            contrasena = input("Contraseña: ")
            contrasena_2 = input("Contraseña confirmación: ")

        try:
            if SalonCSV.filter_by_usuario(usuario):
                print(f"Error: El usuario '{usuario}' ya está registrado.")
                exit()

            SalonCSV.add(nombre=nombre, usuario=usuario, contrasena=contrasena, es_admin=True)
            print(f"\n¡Éxito! El administrador '{usuario}' ha sido creado correctamente en la base de datos PostgreSQL.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al crear el administrador: {e}")

exit()
