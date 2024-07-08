
/*=============================================
EDITAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnEditarUsuario", function () {

	var idUsuario = $(this).attr("idUsuario");

	var datos = new FormData();
	datos.append("idUsuario", idUsuario);

	$.ajax({

		url: "ajax/usuarios.ajax.php",
		method: "POST",
		data: datos,
		cache: false,
		contentType: false,
		processData: false,
		dataType: "json",
		success: function (respuesta) {

			$("#editarNombre").val(respuesta["nombre"]);
			$("#editarUsuario").val(respuesta["usuario"]);
			$("#editarPerfil").html(respuesta["perfil"]);
			$("#editarPerfil").val(respuesta["perfil"]);
			$("#fotoActual").val(respuesta["foto"]);

			$("#passwordActual").val(respuesta["password"]);

			if (respuesta["foto"] != "") {

				$(".previsualizarEditar").attr("src", respuesta["foto"]);

			} else {

				$(".previsualizarEditar").attr("src", "vistas/img/usuarios/default/anonymous.png");

			}

		}

	});

})

/*=============================================
ELIMINAR USUARIO
=============================================*/
$(".tablas").on("click", ".btnEliminarPlantilla", function () {

	var idPlantilla = $(this).attr("idPlantilla");


	Swal.fire({
		title: '¿Está seguro de borrar este dato?',
		text: "¡Si no lo está puede cancelar la accíón!",
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		cancelButtonText: 'Cancelar',
		confirmButtonText: 'Si, borrar plantilla!'
	}).then(function (result) {

		if (result.value) {


			$.ajax({
				url: '/delete_plantilla',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ idPlantilla: idPlantilla }),
				success: function (response) {
					Swal.fire(
						'¡Borrado!',
						'La plantilla ha sido borrada.',
						'success'
					).then(() => {
						// Recargar la página para actualizar la lista de usuarios
						location.reload();
					});
				},
				error: function (xhr, status, error) {
					Swal.fire(
						'Error',
						'Hubo un problema al borrar este dato.',
						'error'
					);
				}
			});

		}

	})

})




$('#userForm input').on("change", function () {
	console.log($(this).attr('value')); // based on the value do something.

	var dato = $(this).attr('value');

	if (dato == "masculino") {

		$(".previsualizar").attr("src", "../assets/images/hombre.png");

		// Asigna la ruta al input file
		$('#nuevaFotoOculta').val("../assets/images/hombre.png");



	}
	else if (dato == "femenino") {

		$(".previsualizar").attr("src", "../assets/images/mujer.png");

		$('#nuevaFotoOculta').val("../assets/images/mujer.png");

	}

	// Redimensionar la imagen a 512x512 píxeles
	$(".previsualizar").css({
		width: "80px",
		height: "80px",
		objectFit: "cover" // Mantener la relación de aspecto de la imagen
	});

});


