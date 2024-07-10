/*=============================================
			AL INICIAR LA PAGINA
=============================================*/
$(document).ready(function () {

	function updateValue(inputId, labelId) {
		$('#' + labelId).text($('#' + inputId).val());
		$('#' + inputId).on('input', function () {
			$('#' + labelId).text($(this).val());

			$.ajax({
				url: '/set_controles',
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
				success: function (response) {
					// Puedes manejar la respuesta si es necesario
					console.log(response.message);
				}
			});

		});

	}


	function defaultValue(inputId, labelId) {

		$('#' + labelId).text($('#' + inputId).val());

		$.ajax({
			url: '/set_controles',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	}

	updateValue('lower-h', 'lower-h-val');
	updateValue('lower-s', 'lower-s-val');
	updateValue('lower-v', 'lower-v-val');
	updateValue('upper-h', 'upper-h-val');
	updateValue('upper-s', 'upper-s-val');
	updateValue('upper-v', 'upper-v-val');

	updateValue('lower-h-dedos', 'lower-h-dedos-val');
	updateValue('lower-s-dedos', 'lower-s-dedos-val');
	updateValue('lower-v-dedos', 'lower-v-dedos-val');
	updateValue('upper-h-dedos', 'upper-h-dedos-val');
	updateValue('upper-s-dedos', 'upper-s-dedos-val');
	updateValue('upper-v-dedos', 'upper-v-dedos-val');

	$('#btnDefault').click(function () {


		/*
		$('#lower-h').val(30)
		$('#lower-s').val(16)
		$('#lower-v').val(103)

		$('#upper-h').val(94)
		$('#upper-s').val(255)
		$('#upper-v').val(255)

		$('#lower-h-dedos').val(40)
		$('#lower-s-dedos').val(16)
		$('#lower-v-dedos').val(87)

		$('#upper-h-dedos').val(100)
		$('#upper-s-dedos').val(255)
		$('#upper-v-dedos').val(255)
		*/

		$.ajax({
			url: '/get_hsv',
			type: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({
				"lower-h": $('#lower-h').val(),
				"lower-s": $('#lower-s').val(),
				"lower-v": $('#lower-v').val(),
				"upper-h": $('#upper-h').val(),
				"upper-s": $('#upper-s').val(),
				"upper-v": $('#upper-v').val(),
				"lower-h-dedos": $('#lower-h-dedos').val(),
				"lower-s-dedos": $('#lower-s-dedos').val(),
				"lower-v-dedos": $('#lower-v-dedos').val(),
				"upper-h-dedos": $('#upper-h-dedos').val(),
				"upper-s-dedos": $('#upper-s-dedos').val(),
				"upper-v-dedos": $('#upper-v-dedos').val()

			}),
			success: function (response) {

				if (response.status == "success") {


				}
				else {
					Swal.fire(
						'Error',
						'Hubo un problema al obtener de configuracion los valores: ' + response.message,
						'error'
					);
				}



			},
			error: function (xhr, status, error) {
				Swal.fire(
					'Error',
					'Hubo un problema al actualizar los valores: ' + error,
					'error'
				);
			}
		});


		defaultValue("lower-h", 'lower-h-val')
		defaultValue("lower-s", 'lower-s-val')
		defaultValue("lower-v", 'lower-v-val')
		defaultValue("upper-h", 'upper-h-val')
		defaultValue("upper-s", 'upper-s-val')
		defaultValue("upper-v", 'upper-v-val')

		defaultValue("lower-h-dedos", 'lower-h-dedos-val')
		defaultValue("lower-s-dedos", 'lower-s-dedos-val')
		defaultValue("lower-v-dedos", 'lower-v-dedos-val')
		defaultValue("upper-h-dedos", 'upper-h-dedos-val')
		defaultValue("upper-s-dedos", 'upper-s-dedos-val')
		defaultValue("upper-v-dedos", 'upper-v-dedos-val')
	});


	$('#btnSaveValues').click(function () {

		Swal.fire({
			title: '¿Está seguro que desea guardar estos valores HSV?',
			text: "¡Si no lo está puede cancelar la accíón!",
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			cancelButtonText: 'Cancelar',
			confirmButtonText: 'Si, guardar!'
		}).then(function (result) {

			if (result.value) {

				$.ajax({
					url: '/save_hsv',
					type: 'POST',
					contentType: 'application/json',
					data: JSON.stringify({
						"lower-h": $('#lower-h').val(),
						"lower-s": $('#lower-s').val(),
						"lower-v": $('#lower-v').val(),
						"upper-h": $('#upper-h').val(),
						"upper-s": $('#upper-s').val(),
						"upper-v": $('#upper-v').val(),
						"lower-h-dedos": $('#lower-h-dedos').val(),
						"lower-s-dedos": $('#lower-s-dedos').val(),
						"lower-v-dedos": $('#lower-v-dedos').val(),
						"upper-h-dedos": $('#upper-h-dedos').val(),
						"upper-s-dedos": $('#upper-s-dedos').val(),
						"upper-v-dedos": $('#upper-v-dedos').val()

					}),
					success: function (response) {

						if (response.status == "success") {
							Swal.fire(
								'¡Guardado!',
								'Los nuevos valores HSV fueron actualizados',
								'success'
							).then(() => {
								// Recargar la página para actualizar la lista de usuarios
								//location.reload();
							});
						}
						else {
							Swal.fire(
								'Error',
								'Hubo un problema al actualizar los valores: ' + response.message,
								'error'
							);
						}



					},
					error: function (xhr, status, error) {
						Swal.fire(
							'Error',
							'Hubo un problema al actualizar los valores: ' + error,
							'error'
						);
					}
				});

			}

		})


	});



	function isEmpty(str) {
		return (!str || str.length === 0);
	}


	var socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('status_update', function (data) {
		if (data) {


			if (isNaN(data.Pizquierdo)) {
				$('#valorIzquierdo').text("---");
			}
			else {
				$('#valorIzquierdo').text(Math.round(data.Pizquierdo) + "%");
			}

			if (isNaN(data.Pderecho)) {
				$('#valorDerecho').text("---");
			}
			else {
				$('#valorDerecho').text(Math.round(data.Pderecho) + "%");
			}


			if (isEmpty(data.Tizquierdo)) {
				$('#tipoIzquierdo').text("");
			}
			else {

				$('#tipoIzquierdo').text("Pie " + data.Tizquierdo);
			}


			if (isEmpty(data.Tderecho)) {
				$('#tipoDerecho').text("");
			}

			else {
				$('#tipoDerecho').text("Pie " + data.Tderecho);
			}





			if (data.txtBien == "MAL") {
				$('#txtColocar').show()
			}
			if (data.txtBien == "BIEN") {
				$('#txtColocar').hide()
			}


		}
	});

	socket.on('status_hsv', function (data) {
		if (data) {

			var variable = data.variables[0]; // Acceder a la primera fila de resultados


			$('#lower-h').val(variable[1]);
			$('#lower-s').val(variable[2]);
			$('#lower-v').val(variable[3]);

			$('#upper-h').val(variable[4]);
			$('#upper-s').val(variable[5]);
			$('#upper-v').val(variable[6]);

			$('#lower-h-dedos').val(variable[7]);
			$('#lower-s-dedos').val(variable[8]);
			$('#lower-v-dedos').val(variable[9]);

			$('#upper-h-dedos').val(variable[10]);
			$('#upper-s-dedos').val(variable[11]);
			$('#upper-v-dedos').val(variable[12]);

			defaultValue("lower-h", 'lower-h-val');
			defaultValue("lower-s", 'lower-s-val');
			defaultValue("lower-v", 'lower-v-val');
			defaultValue("upper-h", 'upper-h-val');
			defaultValue("upper-s", 'upper-s-val');
			defaultValue("upper-v", 'upper-v-val');

			defaultValue("lower-h-dedos", 'lower-h-dedos-val');
			defaultValue("lower-s-dedos", 'lower-s-dedos-val');
			defaultValue("lower-v-dedos", 'lower-v-dedos-val');
			defaultValue("upper-h-dedos", 'upper-h-dedos-val');
			defaultValue("upper-s-dedos", 'upper-s-dedos-val');
			defaultValue("upper-v-dedos", 'upper-v-dedos-val');

		}
	});



	$('#siImagen').click(function () {

		var estadoCheck = "False"

		if ($(this).is(':checked') == true) {
			//alert(estadoCheck);
			estadoCheck = "True"

		} else {
			//alert(estadoCheck);
			estadoCheck = "False"
		}

		$.ajax({
			url: '/set_check',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ check: estadoCheck }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	});


	$('#btnCapturar').click(function () {


		$.ajax({
			url: '/set_imagen',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ estado: "ON" }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});
	});


	$('#btnReproducir').click(function () {



		$.ajax({
			url: '/set_imagen',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ estado: "OFF" }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});
	});


	$('#btnGuardar').click(function () {

		Swal.fire({
			title: '¿Está seguro que deseas guardar esta prueba?',
			text: "¡Si no lo está puede cancelar la accíón!",
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			cancelButtonText: 'Cancelar',
			confirmButtonText: 'Si, guardar!'
		}).then(function (result) {

			if (result.value) {

				$.ajax({
					url: '/set_guardar',
					type: 'POST',
					contentType: 'application/json',
					data: JSON.stringify({ estado: "ON" }),
					success: function (response) {

						if (response.status == "success") {
							Swal.fire(
								'¡Guardado!',
								'La prueba se guardo correctamente',
								'success'
							).then(() => {
								// Recargar la página para actualizar la lista de usuarios
								//location.reload();
							});
						}
						else {
							Swal.fire(
								'Error',
								'Hubo un problema al guardar la prueba: ' + response.message,
								'error'
							);
						}



					},
					error: function (xhr, status, error) {
						Swal.fire(
							'Error',
							'Hubo un problema al guardar la prueba: ' + error,
							'error'
						);
					}
				});

			}

		})






	});





	$('.tipoVideo').on('change', function () {
		console.log(this.value);
		const selectedValue = this.value;

		if (selectedValue == "normal") {
			$('#contenedorControles').hide();
			$('#contenedorPies').hide();
			$('#contenedorBotones').hide();
		}

		else {
			$('#contenedorControles').show();
			$('#contenedorPies').show();
			$('#contenedorBotones').show();
		}

		$.ajax({
			url: '/set_mode',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ mode: selectedValue }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
		});

	});


});


